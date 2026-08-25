# Tạo model work item

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from datetime import datetime
from app.db.database import Base

status_enum = Enum("TODO", "IN_PROGRESS", "DONE", name="work_item_status")
priority_enum = Enum("LOW", "MEDIUM", "HIGH", name="work_item_priority")
# Đây là tạo kiểu enum

class WorkItem(Base):
    __tablename__ = "work_items"
    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("construction_sites.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(status_enum, default="TODO", nullable=False)
    priority = Column(priority_enum, default="MEDIUM", nullable=False)
    due_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)