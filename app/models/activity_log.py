from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from datetime import datetime

from app.db.database import Base

# Model lưu lịch sử hoạt động của hệ thống
class ActivityLog(Base):
    __tablename__ = "activity_logs"

    # ID của log
    id = Column(Integer, primary_key=True, index=True)

    # ID công trình mà thao tác xảy ra
    site_id = Column(
        Integer,
        ForeignKey("construction_sites.id"),
        nullable=False
    )

    # ID user thực hiện thao tác
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    # Loại thao tác
    # Ví dụ: CREATE_SITE, UPDATE_SITE, ADD_MEMBER, REMOVE_MEMBER
    action = Column(String(50), nullable=False)

    # Nội dung mô tả thao tác
    description = Column(Text, nullable=False)

    # Thời gian thực hiện
    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )