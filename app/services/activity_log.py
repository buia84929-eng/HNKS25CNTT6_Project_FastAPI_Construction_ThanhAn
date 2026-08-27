from sqlalchemy.orm import Session

from app.models.activity_log import ActivityLog

def create_activity_log(
    db: Session,
    user_id: int,
    site_id: int | None,
    action: str,
    description: str
):
    # Tạo một bản ghi lịch sử thao tác
    log = ActivityLog(
        user_id=user_id,
        site_id=site_id,
        action=action,
        description=description
    )

    # Thêm log vào database
    db.add(log)

    # Lưu log xuống database
    db.commit()