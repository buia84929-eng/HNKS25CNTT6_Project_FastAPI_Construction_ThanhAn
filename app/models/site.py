from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.database import Base

# model công trình
class ConstructionSite(Base):
    __tablename__ = "construction_sites"

    # ID của công trình
    id = Column(Integer, primary_key=True, index=True)

    # Tên công trình
    name = Column(String(255), nullable=False)

    # Mô tả công trình
    description = Column(Text, nullable=True)

    # ID của người sở hữu công trình
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Thời gian tạo công trình
    created_at = Column(DateTime, default=datetime.utcnow)

    # Quan hệ với bảng User
    owner = relationship("User")

    # Quan hệ với bảng SiteMember
    members = relationship("SiteMember", back_populates="site", cascade="all, delete-orphan")

# model thành viên công trình
class SiteMember(Base):
    __tablename__ = "site_members"

    # ID của công trình
    site_id = Column(Integer, ForeignKey("construction_sites.id"), primary_key=True)

    # ID của user
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)

    # Vai trò trong công trình
    # OWNER hoặc MEMBER
    role = Column(String(20), nullable=False)

    # Thời gian tham gia
    joined_at = Column(DateTime, default=datetime.utcnow)

    # Quan hệ ngược về công trình
    site = relationship("ConstructionSite", back_populates="members")

    # Quan hệ ngược về User
    user = relationship("User")