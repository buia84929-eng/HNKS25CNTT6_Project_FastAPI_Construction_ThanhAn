from pydantic import BaseModel, ConfigDict
from datetime import datetime

# TẠO HẠNG MỤC
class WorkItemCreate(BaseModel):
    # Tiêu đề công việc
    title: str
    # Mô tả công việc (không bắt buộc)
    description: str | None = None
    # Người được giao
    assignee_id: int | None = None
    # Độ ưu tiên
    priority: str = "MEDIUM"
    # Hạn hoàn thành
    due_date: datetime | None = None

# CẬP NHẬT HẠNG MỤC
class WorkItemUpdate(BaseModel):
    # Các trường đều optional vì PATCH
    title: str | None = None
    description: str | None = None
    assignee_id: int | None = None
    priority: str | None = None
    status: str | None = None
    due_date: datetime | None = None

# RESPONSE
class WorkItemResponse(BaseModel):

    id: int
    site_id: int
    title: str
    description: str | None
    assignee_id: int | None
    status: str
    priority: str
    due_date: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)