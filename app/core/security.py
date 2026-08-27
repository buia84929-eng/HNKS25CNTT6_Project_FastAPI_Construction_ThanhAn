from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

# BCRYPT - DÙNG ĐỂ BĂM VÀ KIỂM TRA MẬT KHẨU
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

def hash_password(password: str) -> str:
    # Chuyển mật khẩu dạng thường thành mật khẩu đã được băm
    return pwd_context.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    # Kiểm tra mật khẩu người dùng nhập
    # có khớp với mật khẩu đã băm trong database hay không
    return pwd_context.verify(password, password_hash)


# ACCESS TOKEN
def create_access_token(data: dict) -> str:
    # Tạo bản sao dữ liệu để không làm thay đổi dữ liệu gốc
    to_encode = data.copy()

    # Tính thời gian hết hạn của access token
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    # Thêm thời gian hết hạn vào JWT
    to_encode.update({
        "exp": expire,
        "type": "access"
    })

    # Tạo JWT bằng SECRET_KEY
    token = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return token

def decode_access_token(token: str):
    # Giải mã JWT và kiểm tra chữ ký + thời gian hết hạn
    payload = jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM]
    )

    # Chỉ cho phép token có type = access
    if payload.get("type") != "access":
        return None

    return payload


# REFRESH TOKEN
def create_refresh_token(data: dict) -> str:
    # Tạo bản sao dữ liệu
    to_encode = data.copy()

    # Refresh token sống lâu hơn access token
    # Ở đây đặt thời gian sống là 7 ngày
    expire = datetime.now(timezone.utc) + timedelta(days=7)

    # Gắn thời gian hết hạn và loại token
    to_encode.update({
        "exp": expire,
        "type": "refresh"
    })

    # Tạo refresh token
    token = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return token

def decode_refresh_token(token: str):
    # Giải mã refresh token
    payload = jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM]
    )

    # Kiểm tra token có đúng là refresh token không
    if payload.get("type") != "refresh":
        return None

    return payload