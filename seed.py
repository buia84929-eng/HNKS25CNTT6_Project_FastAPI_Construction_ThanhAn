from app.db.database import SessionLocal
from app.models.user import User
from app.models.site import ConstructionSite, SiteMember
from app.models.works_item import WorkItem
from app.core.security import hash_password

# Tạo database session
db = SessionLocal()

try:
    # 1. TẠO USER MẪU
    user1 = User(
        email="admin@gmail.com",
        password_hash=hash_password("123"),
        full_name="Admin",
        role="ADMIN",
        is_active=True
    )

    user2 = User(
        email="user@gmail.com",
        password_hash=hash_password("123"),
        full_name="Nguyen Van A",
        role="USER",
        is_active=True
    )

    user3 = User(
    email="outsider@gmail.com",
    password_hash=hash_password("123"),
    full_name="Nguyen Van B",
    role="USER",
    is_active=True
    )

    # Thêm user vào database
    db.add(user1)
    db.add(user2)
    db.add(user3)

    # Commit để database tạo ID cho user
    db.commit()

    # Refresh để lấy ID vừa được database tạo
    db.refresh(user1)
    db.refresh(user2)
    db.refresh(user3)

    # 2. TẠO CÔNG TRÌNH MẪU
    site = ConstructionSite(
        name="Công trình Nhà ở ABC",
        description="Công trình nhà ở mẫu",
        owner_id=user1.id
    )

    db.add(site)
    db.commit()
    db.refresh(site)

    # 3. THÊM THÀNH VIÊN VÀO CÔNG TRÌNH
    member1 = SiteMember(
        site_id=site.id,
        user_id=user1.id,
        role="OWNER"
    )

    member2 = SiteMember(
        site_id=site.id,
        user_id=user2.id,
        role="MEMBER"
    )

    db.add(member1)
    db.add(member2)

    db.commit()

    # 4. TẠO WORK ITEM MẪU
    work1 = WorkItem(
        site_id=site.id,
        title="Chuẩn bị mặt bằng",
        description="Dọn dẹp và chuẩn bị mặt bằng xây dựng",
        assignee_id=user2.id,
        status="TODO",
        priority="HIGH"
    )

    work2 = WorkItem(
        site_id=site.id,
        title="Thi công móng",
        description="Thi công phần móng công trình",
        assignee_id=user2.id,
        status="IN_PROGRESS",
        priority="MEDIUM"
    )

    work3 = WorkItem(
        site_id=site.id,
        title="Kiểm tra công trình",
        description="Kiểm tra tiến độ và chất lượng công trình",
        assignee_id=user1.id,
        status="DONE",
        priority="LOW"
    )

    db.add(work1)
    db.add(work2)
    db.add(work3)

    db.commit()

    print("Seed dữ liệu thành công!")
    print("Đã tạo:")
    print("- 2 user")
    print("- 1 công trình")
    print("- 2 thành viên công trình")
    print("- 3 work item")

except Exception as e:
    # Nếu có lỗi thì hủy các thay đổi chưa lưu
    db.rollback()
    print("Seed dữ liệu thất bại:", e)

finally:
    # Đóng database session
    db.close()