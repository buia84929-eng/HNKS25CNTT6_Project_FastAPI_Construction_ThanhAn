from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

# schemas tạo công trình
class SiteCreate(BaseModel):
    # Tên công trình không được để trống
    name: str = Field(
        min_length=1,
        max_length=255
    )

    # Mô tả có thể bỏ trống
    description: str | None = None

#schemas cập nhật công trình
class SiteUpdate(BaseModel):
    # Optional vì PATCH chỉ cập nhật
    # những trường người dùng gửi lên
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255
    )

    description: str | None = None

#schemas trả về công trình
class SiteResponse(BaseModel):
    id: int
    name: str
    description: str | None
    owner_id: int
    created_at: datetime

    # Cho phép Pydantic đọc dữ liệu
    # từ SQLAlchemy model
    model_config = ConfigDict(
        from_attributes=True
    )

# schemas thêm member
class MemberCreate(BaseModel):
    # ID của user muốn thêm vào công trình
    user_id: int

# schemas trả về member
class MemberResponse(BaseModel):
    user_id: int
    email: str
    full_name: str
    role: str
    joined_at: datetime