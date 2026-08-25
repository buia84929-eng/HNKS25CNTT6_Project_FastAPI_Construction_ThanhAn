from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)
# Dùng bcrypt để băm mật khẩu

def hash_password(password: str) -> str:
    return pwd_context.hash(password)
    # Chuyển mật khẩu thường thành mật khẩu đã hash

def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)
    # Kiểm tra mật khẩu người dùng nhập có đúng với mật khẩu đã hash hay không

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    # Tạo bản sao dữ liệu để không làm thay đổi dữ liệu ban đầu

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    # Tính thời gian hết hạn của token

    to_encode.update({"exp": expire})
    # Thêm thời gian hết hạn vào token

    token = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    ) # Tạo JWT

    return token

def decode_access_token(token: str):
    return jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM]
    )
    # Giải mã và kiểm tra JWT