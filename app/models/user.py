from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from app.db.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True) # mã user
    email = Column(String(255), unique=True, nullable=False) # email
    password_hash = Column(String(255), nullable=False) # mật khẩu đã hash
    full_name = Column(String(100), nullable=False) # họ tên
    role = Column(String(20), default="USER") # user/admin
    is_active = Column(Boolean, default=True) # tài khoản còn hoạt động
    created_at = Column(DateTime, default=datetime.utcnow) # ngày tạo