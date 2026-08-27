from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.dependencies.auth import get_current_user

from app.models.user import User
from app.models.site import ConstructionSite, SiteMember
from app.models.works_item import WorkItem

from app.schemas.work_item import (
    WorkItemCreate,
    WorkItemUpdate,
    WorkItemResponse
)

router = APIRouter(
    prefix="/work-items",
    tags=["Work Items"]
)

# API tạo work_item
@router.post(
    "/construction-sites/{site_id}",
    response_model=WorkItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo hạng mục công việc",
    description="Tạo một hạng mục công việc thuộc công trình."
)
def create_work_item(
    site_id: int,
    work_data: WorkItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # Kiểm tra công trình có tồn tại không
    site = db.query(ConstructionSite).filter(
        ConstructionSite.id == site_id
    ).first()

    if site is None:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy công trình"
        )

    # Kiểm tra user có thuộc công trình không
    member = db.query(SiteMember).filter(
        SiteMember.site_id == site_id,
        SiteMember.user_id == current_user.id
    ).first()

    # ADMIN được tạo WorkItem
    if current_user.role != "ADMIN":

        # OWNER được tạo WorkItem
        is_owner = site.owner_id == current_user.id

        # MEMBER được tạo WorkItem
        member = db.query(SiteMember).filter(
            SiteMember.site_id == site_id,
            SiteMember.user_id == current_user.id
        ).first()

        # Không phải ADMIN, OWNER hoặc MEMBER
        if not is_owner and member is None:
            raise HTTPException(
                status_code=403,
                detail="Bạn không có quyền tạo hạng mục"
            )

    # Kiểm tra assignee có thuộc công trình không
    if work_data.assignee_id is not None:

        assignee = db.query(SiteMember).filter(
            SiteMember.site_id == site_id,
            SiteMember.user_id == work_data.assignee_id
        ).first()

        if assignee is None:
            raise HTTPException(
                status_code=400,
                detail="Không thể giao việc cho user ngoài công trình"
            )

    # Tạo Work Item
    work_item = WorkItem(
        site_id=site_id,
        title=work_data.title,
        description=work_data.description,
        assignee_id=work_data.assignee_id,
        priority=work_data.priority,
        status="TODO",
        due_date=work_data.due_date
    )

    db.add(work_item)
    db.commit()
    db.refresh(work_item)

    return work_item

# Danh sách work_item
@router.get(
    "/construction-sites/{site_id}",
    response_model=list[WorkItemResponse],
    summary="Danh sách hạng mục",
    description="Lấy danh sách các hạng mục công việc của công trình."
)
def get_work_items(
    site_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # Tìm công trình
    site = db.query(ConstructionSite).filter(
        ConstructionSite.id == site_id
    ).first()

    # Nếu không tìm thấy công trình
    if site is None:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy công trình"
        )

    # ADMIN được xem tất cả công trình
    if current_user.role != "ADMIN":

        # Kiểm tra user có phải OWNER không
        is_owner = site.owner_id == current_user.id

        # Kiểm tra user có phải MEMBER không
        member = db.query(SiteMember).filter(
            SiteMember.site_id == site_id,
            SiteMember.user_id == current_user.id
        ).first()

        # Không phải OWNER và cũng không phải MEMBER
        if not is_owner and member is None:
            raise HTTPException(
                status_code=403,
                detail="Bạn không có quyền xem công trình này"
            )

    works = db.query(WorkItem).filter(
        WorkItem.site_id == site_id
    ).all()

    return works

# Chi tiết work_item
@router.get(
    "/{work_id}",
    response_model=WorkItemResponse,
    summary="Chi tiết hạng mục",
    description="Lấy thông tin chi tiết của một hạng mục công việc."
)
def get_work_item(
    work_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    work = db.query(WorkItem).filter(
        WorkItem.id == work_id
    ).first()

    if work is None:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy hạng mục"
        )

    # Tìm công trình chứa WorkItem
    site = db.query(ConstructionSite).filter(
        ConstructionSite.id == work.site_id
    ).first()

    # ADMIN được xem
    if current_user.role != "ADMIN":

        # Kiểm tra có phải OWNER không
        is_owner = site.owner_id == current_user.id

        # Kiểm tra có phải MEMBER không
        member = db.query(SiteMember).filter(
            SiteMember.site_id == work.site_id,
            SiteMember.user_id == current_user.id
        ).first()

        # Không phải OWNER và cũng không phải MEMBER
        if not is_owner and member is None:
            raise HTTPException(
                status_code=403,
                detail="Bạn không được xem hạng mục này"
            )

    return work

# Cập nhật work_item
@router.patch(
    "/{work_id}",
    response_model=WorkItemResponse,
    summary="Cập nhật hạng mục",
    description="Cập nhật thông tin hạng mục công việc."
)
def update_work_item(
    work_id: int,
    work_data: WorkItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    work = db.query(WorkItem).filter(
        WorkItem.id == work_id
    ).first()

    if work is None:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy hạng mục"
        )

    # Chỉ Owner hoặc Assignee được sửa
    site = db.query(ConstructionSite).filter(
        ConstructionSite.id == work.site_id
    ).first()

    if (
        site.owner_id != current_user.id
        and work.assignee_id != current_user.id
    ):
        raise HTTPException(
            status_code=403,
            detail="Bạn không có quyền sửa"
        )

    # PATCH: chỉ sửa trường được gửi lên
    if work_data.title is not None:
        work.title = work_data.title

    if work_data.description is not None:
        work.description = work_data.description

    if work_data.assignee_id is not None:
        work.assignee_id = work_data.assignee_id

    if work_data.priority is not None:
        work.priority = work_data.priority

    if work_data.status is not None:
        work.status = work_data.status

    if work_data.due_date is not None:
        work.due_date = work_data.due_date

    db.commit()
    db.refresh(work)

    return work

# Xóa work_item
@router.delete(
    "/{work_id}",
    summary="Xóa hạng mục",
    description="Xóa một hạng mục công việc. Chỉ OWNER mới có quyền xóa."
)
def delete_work_item(
    work_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    work = db.query(WorkItem).filter(
        WorkItem.id == work_id
    ).first()

    if work is None:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy hạng mục"
        )

    site = db.query(ConstructionSite).filter(
        ConstructionSite.id == work.site_id
    ).first()

    if site.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Chỉ Owner được xóa"
        )

    db.delete(work)
    db.commit()

    return {
        "message":"Xóa thành công"
    }

# Search, filter
@router.get(
    "/construction-sites/{site_id}/search",
    response_model=list[WorkItemResponse],
    summary="Tìm kiếm và lọc hạng mục",
    description="Tìm kiếm theo tên và lọc hạng mục theo status, priority, assignee. Có hỗ trợ phân trang."
)
def search_work_items(
    site_id: int,

    # Tìm theo tên công việc
    title: str | None = None,

    # Lọc theo trạng thái
    status: str | None = None,

    # Lọc theo độ ưu tiên
    priority: str | None = None,

    # Lọc theo người được giao
    assignee_id: int | None = None,

    # Phân trang
    # limit: số lượng công việc muốn lấy
    limit: int = 10,

    # offset: bỏ qua bao nhiêu công việc đầu tiên
    offset: int = 0,

    # Sort theo trường nào
    # Có thể là created_at hoặc due_date
    sort_by: str = "created_at",

    # Thứ tự sort
    # asc = tăng dần
    # desc = giảm dần
    sort_order: str = "desc",

    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # Tìm công trình
    site = db.query(ConstructionSite).filter(
        ConstructionSite.id == site_id
    ).first()

    # Nếu công trình không tồn tại
    if site is None:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy công trình"
        )

    # ADMIN được xem tất cả công trình
    if current_user.role != "ADMIN":

        # Kiểm tra user có phải OWNER không
        is_owner = site.owner_id == current_user.id

        # Kiểm tra user có phải MEMBER không
        member = db.query(SiteMember).filter(
            SiteMember.site_id == site_id,
            SiteMember.user_id == current_user.id
        ).first()

        # Nếu không phải OWNER và cũng không phải MEMBER
        # thì không có quyền xem
        if not is_owner and member is None:
            raise HTTPException(
                status_code=403,
                detail="Không có quyền"
            )

    # Bắt đầu tìm các WorkItem của công trình
    query = db.query(WorkItem).filter(
        WorkItem.site_id == site_id
    )

    # SEARCH THEO TÊN

    if title:
        query = query.filter(
            WorkItem.title.ilike(f"%{title}%")
        )

    # FILTER THEO TRẠNG THÁI

    if status:
        query = query.filter(
            WorkItem.status == status
        )

    # FILTER THEO ĐỘ ƯU TIÊN

    if priority:
        query = query.filter(
            WorkItem.priority == priority
        )

    # FILTER THEO NGƯỜI ĐƯỢC GIAO

    if assignee_id:
        query = query.filter(
            WorkItem.assignee_id == assignee_id
        )

    # SORT

    # Sắp xếp theo ngày tạo mới nhất trước
    query = query.order_by(
        WorkItem.created_at.desc()
    )

    # SORT

    # Chỉ cho phép sort theo 2 trường mà đề bài yêu cầu
    if sort_by not in ["created_at", "due_date"]:
        raise HTTPException(
            status_code=400,
            detail="sort_by chỉ được là created_at hoặc due_date"
        )

    # Chỉ cho phép 2 kiểu sắp xếp
    if sort_order not in ["asc", "desc"]:
        raise HTTPException(
            status_code=400,
            detail="sort_order chỉ được là asc hoặc desc"
        )

    # Sắp xếp theo created_at

    if sort_by == "created_at":

        if sort_order == "asc":
            # Cũ -> mới
            query = query.order_by(
                WorkItem.created_at.asc()
            )

        else:
            # Mới -> cũ
            query = query.order_by(
                WorkItem.created_at.desc()
            )

    # Sắp xếp theo due_date

    elif sort_by == "due_date":

        if sort_order == "asc":
            # Hạn gần -> hạn xa
            query = query.order_by(
                WorkItem.due_date.asc()
            )

        else:
            # Hạn xa -> hạn gần
            query = query.order_by(
                WorkItem.due_date.desc()
            )

    # PHÂN TRANG

    # offset: bỏ qua bao nhiêu bản ghi
    # limit: lấy tối đa bao nhiêu bản ghi
    query = query.offset(offset).limit(limit)

    # Trả về kết quả
    return query.all()