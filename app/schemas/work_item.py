from datetime import datetime
from pydantic import BaseModel

class WorkItemBase(BaseModel):
    title: str
    description: str | None = None
    assignee_id: int | None = None
    status: str = "TODO"
    priority: str = "MEDIUM"
    due_date: datetime | None = None
# Thông tin cơ bản của công việc

class WorkItemCreate(WorkItemBase):
    pass
# Dùng khi tạo công việc mới

class WorkItemUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    assignee_id: int | None = None
    status: str | None = None
    priority: str | None = None
    due_date: datetime | None = None
# Dùng khi cập nhật công việc

class WorkItemResponse(WorkItemBase):
    id: int
    site_id: int
    created_at: datetime
# Dữ liệu trả về cho client

    class Config:
        from_attributes = True
    # Cho phép Pydantic đọc dữ liệu từ SQL
