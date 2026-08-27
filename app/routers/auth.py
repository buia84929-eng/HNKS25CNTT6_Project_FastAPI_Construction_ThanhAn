from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_refresh_token
)

from app.db.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# RATE LIMIT - GIỚI HẠN SỐ LẦN LOGIN

# Lưu số lần đăng nhập sai của từng IP
login_attempts = {}

# Số lần đăng nhập sai tối đa
MAX_LOGIN_ATTEMPTS = 5

# Thời gian khóa login sau khi vượt quá giới hạn
LOCK_TIME = timedelta(minutes=1)


# SCHEMA CHO REFRESH TOKEN
class RefreshTokenRequest(BaseModel):
    # Client gửi refresh token lên API
    refresh_token: str


# REGISTER
@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Đăng ký tài khoản",
    description="Tạo tài khoản người dùng mới bằng email, họ tên và mật khẩu."
)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    # Kiểm tra email đã tồn tại chưa
    existing_user = db.query(User).filter(
        User.email == user_data.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email đã tồn tại"
        )

    # Tạo user mới
    user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        password_hash=hash_password(user_data.password),
        role="USER",
        is_active=True
    )

    # Lưu user vào database
    db.add(user)
    db.commit()
    db.refresh(user)

    return user


# LOGIN
@router.post(
    "/login",
    summary="Đăng nhập",
    description="Kiểm tra email và mật khẩu, sau đó trả về Access Token JWT."
)
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # Lấy địa chỉ IP của người đang gọi API
    client_ip = request.client.host

    # Lấy thông tin số lần login của IP này
    attempt = login_attempts.get(
        client_ip,
        {
            "count": 0,
            "last_attempt": datetime.now()
        }
    )


    # KIỂM TRA RATE LIMIT

    # Nếu IP đã bị khóa
    if attempt["count"] >= MAX_LOGIN_ATTEMPTS:

        # Kiểm tra đã hết thời gian khóa chưa
        if datetime.now() - attempt["last_attempt"] < LOCK_TIME:

            # Chưa hết thời gian → không cho login tiếp
            raise HTTPException(
                status_code=429,
                detail="Bạn đăng nhập quá nhiều lần. Vui lòng thử lại sau 1 phút."
            )

        # Nếu đã hết 1 phút thì cho phép thử lại
        attempt = {
            "count": 0,
            "last_attempt": datetime.now()
        }


    # TÌM USER
    user = db.query(User).filter(
        User.email == form_data.username
    ).first()

    # Nếu không tìm thấy user
    if user is None:

        # Tăng số lần đăng nhập sai
        attempt["count"] += 1
        attempt["last_attempt"] = datetime.now()

        login_attempts[client_ip] = attempt

        raise HTTPException(
            status_code=401,
            detail="Email hoặc mật khẩu không đúng"
        )


    # KIỂM TRA PASSWORD
    if not verify_password(
        form_data.password,
        user.password_hash
    ):

        # Sai password → tăng số lần thử
        attempt["count"] += 1
        attempt["last_attempt"] = datetime.now()

        login_attempts[client_ip] = attempt

        raise HTTPException(
            status_code=401,
            detail="Email hoặc mật khẩu không đúng"
        )

    # KIỂM TRA TÀI KHOẢN
    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="Tài khoản đã bị khóa"
        )

    # LOGIN THÀNH CÔNG
    # Login đúng → xóa số lần login sai của IP
    login_attempts.pop(client_ip, None)

    # Tạo access token
    access_token = create_access_token({
        "sub": str(user.id)
    })

    # Tạo refresh token
    refresh_token = create_refresh_token({
        "sub": str(user.id)
    })

    # Trả về cả 2 token
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


# REFRESH TOKEN
@router.post("/refresh")
def refresh_access_token(
    data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    # Giải mã refresh token
    payload = decode_refresh_token(data.refresh_token)

    # Nếu token không hợp lệ
    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Refresh token không hợp lệ"
        )

    # Lấy user_id từ trường sub
    user_id = payload.get("sub")

    # Nếu token không có user_id
    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Refresh token không hợp lệ"
        )

    # Tìm user trong database
    user = db.query(User).filter(
        User.id == int(user_id)
    ).first()

    # User không tồn tại
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User không tồn tại"
        )

    # User bị khóa thì không được cấp token mới
    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="Tài khoản đã bị khóa"
        )

    # Tạo access token mới
    new_access_token = create_access_token({
        "sub": str(user.id)
    })

    # Trả access token mới
    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }