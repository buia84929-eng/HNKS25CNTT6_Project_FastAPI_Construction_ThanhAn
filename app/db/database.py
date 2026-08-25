# File để kết nối với MySQL

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
# Kết nối Python với MySQL

SessionLocal = sessionmaker(
    autocommit = False,
    autoflush = False,
    bind = engine
)
# Tạo phiên làm việc với database

Base = declarative_base()
# Các model sau này sẽ kế thừa từ Base

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally: 
        db.close()