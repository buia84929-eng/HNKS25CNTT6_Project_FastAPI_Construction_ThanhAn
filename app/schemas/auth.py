# Tạo schemas cho login/token

from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str
    # Dữ liệu trả về sau khi đăng nhập thành công

class TokenData(BaseModel):
    user_id: int | None = None
    # Dữ liệu cơ bản lấy từ JWT