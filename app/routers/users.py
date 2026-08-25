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
    response_model=UserResponse
)
def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    # Trả thông tin của user đang đăng nhập
    return current_user

@router.get(
    "",
    response_model=list[UserResponse]
)
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    # Chỉ ADMIN mới có thể xem danh sách user
    users = db.query(User).all()

    return users