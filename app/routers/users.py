from fastapi import APIRouter, Depends
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.user import UserResponse
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.dependencies.auth import require_admin

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.get(
    "/me",
    response_model=UserResponse,
    summary="Xem thông tin cá nhân",
    description="Lấy thông tin của tài khoản đang đăng nhập."
)
def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    # Trả thông tin của user đang đăng nhập
    return current_user


@router.get(
    "",
    response_model=list[UserResponse],
    summary="Danh sách người dùng",
    description="Lấy danh sách người dùng. Chỉ ADMIN được phép truy cập."
)
def get_users(
    name: str | None = None,
    email: str | None = None,
    is_active: bool | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    # Chỉ ADMIN mới có thể xem danh sách user
    query = db.query(User)

    # Tìm theo tên
    if name:
        query = query.filter(
            User.full_name.ilike(f"%{name}%")
        )

    # Tìm theo email
    if email:
        query = query.filter(
            User.email.ilike(f"%{email}%")
        )

    # Lọc theo trạng thái
    if is_active is not None:
        query = query.filter(
            User.is_active == is_active
        )

    return query.all()