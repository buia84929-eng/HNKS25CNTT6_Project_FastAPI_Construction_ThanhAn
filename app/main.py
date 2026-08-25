from fastapi import FastAPI
from sqlalchemy import text

from app.db.database import Base, engine

from app.models.user import User
from app.models.site import ConstructionSite, SiteMember
from app.models.works_item import WorkItem

from app.routers import auth, users, site

# Tạo các bảng trong database
Base.metadata.create_all(bind=engine)

app = FastAPI()

# đăng kí router
# API đăng ký / đăng nhập
app.include_router(auth.router)

# API user
app.include_router(users.router)

# API công trình
app.include_router(site.router)

# test database
@app.get("/test-db")
def test_db():
    # Mở kết nối đến database
    with engine.connect() as connection:

        # Chạy câu SQL đơn giản để kiểm tra
        connection.execute(text("SELECT 1"))
    return {
        "message": "Kết nối Database thành công!"
    }

# check database có hoạt động không
@app.get("/health")
def health_check():

    return {
        "status": "ok"
    }