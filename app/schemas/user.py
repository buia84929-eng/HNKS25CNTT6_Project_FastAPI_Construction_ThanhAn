from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
# Thông tin cơ bản của user

class UserCreate(UserBase):
    password: str
# Dùng khi tạo user, có thêm password

class UserUpdate(BaseModel):
    full_name: str | None = None
# Dùng khi sửa user

class UserResponse(UserBase):
    id: int
    role: str
    is_active: bool
# Dũ liệu trả về cho client
    class Config:
        from_attributes = True
    # Cho phép Pydantic đọc dữ liệu từ SQL