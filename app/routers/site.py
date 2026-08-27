from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.site import ConstructionSite, SiteMember
from app.models.activity_log import ActivityLog
# Import hàm dùng để ghi lịch sử thao tác
from app.services.activity_log import create_activity_log

from app.schemas.site import (
    SiteCreate,
    SiteUpdate,
    SiteResponse,
    MemberCreate,
    MemberResponse
)

# Tạo router cho chức năng công trình
router = APIRouter(
    prefix="/construction-sites",
    tags=["Construction Sites"]
)


# API 1: TẠO CÔNG TRÌNH
# POST /construction-sites
@router.post(
    "",
    response_model=SiteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo công trình",
    description="Tạo một công trình mới và tự động thêm người tạo làm OWNER."
)
def create_site(
    site_data: SiteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Tạo công trình mới
    site = ConstructionSite(
        name=site_data.name,
        description=site_data.description,

        # Người đang đăng nhập sẽ trở thành OWNER
        owner_id=current_user.id
    )

    # Thêm công trình vào database
    db.add(site)

    # Commit để database tạo ID cho site
    db.commit()

    # Lấy lại dữ liệu site sau khi insert
    db.refresh(site)


    # Tạo thành viên OWNER
    owner_member = SiteMember(
        site_id=site.id,
        user_id=current_user.id,
        role="OWNER"
    )

    # Lưu OWNER vào bảng site_members
    db.add(owner_member)

    # Lưu xuống database
    db.commit()

    # Ghi log thao tác tạo công trình
    create_activity_log(
        db=db,
        user_id=current_user.id,
        site_id=site.id,
        action="CREATE_SITE",
        description=f'Tạo công trình "{site.name}"'
    )

    # Trả về công trình vừa tạo
    return site


# API 2: DANH SÁCH CÔNG TRÌNH
# GET /construction-sites
@router.get(
    "",
    response_model=list[SiteResponse],
    summary="Danh sách công trình",
    description="Lấy danh sách các công trình mà người dùng có quyền xem."
)
def get_my_sites(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Tìm các công trình mà user:
    # - là OWNER
    # - hoặc là MEMBER

    sites = (
        db.query(ConstructionSite)
        .join(
            SiteMember,
            SiteMember.site_id == ConstructionSite.id
        )
        .filter(
            SiteMember.user_id == current_user.id
        )
        .all()
    )

    return sites


# API 3: XEM CHI TIẾT CÔNG TRÌNH
# GET /construction-sites/{site_id}
@router.get(
    "/{site_id}",
    response_model=SiteResponse,
    summary="Chi tiết công trình",
    description="Lấy thông tin chi tiết của một công trình."
)
def get_site_detail(
    site_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Tìm công trình trước
    site = (
        db.query(ConstructionSite)
        .filter(
            ConstructionSite.id == site_id
        )
        .first()
    )

    # Không tìm thấy công trình
    if site is None:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy công trình"
        )

    # Kiểm tra user có phải OWNER của công trình không
    is_owner = site.owner_id == current_user.id

    # Kiểm tra user có phải MEMBER của công trình không
    member = (
        db.query(SiteMember)
        .filter(
            SiteMember.site_id == site_id,
            SiteMember.user_id == current_user.id
        )
        .first()
    )

    # OWNER hoặc MEMBER đều được xem
    if not is_owner and member is None:
        raise HTTPException(
            status_code=403,
            detail="Bạn không có quyền xem công trình này"
        )

    return site


# API 4: CẬP NHẬT CÔNG TRÌNH
# PATCH /construction-sites/{site_id}
@router.patch(
    "/{site_id}",
    response_model=SiteResponse,
    summary="Cập nhật công trình",
    description="Cập nhật thông tin công trình. Chỉ OWNER có quyền chỉnh sửa."
)
def update_site(
    site_id: int,
    site_data: SiteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Tìm công trình
    site = (
        db.query(ConstructionSite)
        .filter(
            ConstructionSite.id == site_id
        )
        .first()
    )

    if site is None:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy công trình"
        )

    # Chỉ OWNER mới được sửa
    if site.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Chỉ OWNER mới được sửa công trình"
        )

    # Chỉ cập nhật những trường được gửi lên
    if site_data.name is not None:
        site.name = site_data.name

    if site_data.description is not None:
        site.description = site_data.description

    # Lưu thay đổi
    db.commit()
    db.refresh(site)

    # Ghi log thao tác sửa công trình
    create_activity_log(
        db=db,
        user_id=current_user.id,
        site_id=site.id,
        action="UPDATE_SITE",
        description=f'Cập nhật công trình "{site.name}"'
    )

    return site


# api 5: xóa công trình
# DELETE /construction-sites/{site_id}
@router.delete(
    "/{site_id}",
    summary="Xóa công trình",
    description="Xóa một công trình. Chỉ OWNER mới có quyền thực hiện."
)
def delete_site(
    site_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Tìm công trình
    site = (
        db.query(ConstructionSite)
        .filter(
            ConstructionSite.id == site_id
        )
        .first()
    )
    if site is None:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy công trình"
        )

    # Chỉ OWNER mới được xóa
    if site.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Chỉ OWNER mới được xóa công trình"
        )

    # Xóa công trình
    db.delete(site)
    db.commit()

    return {
        "message": "Xóa công trình thành công"
    }

# api 6: thêm member
# POST /construction-sites/{site_id}/members
@router.post(
    "/{site_id}/members",
    response_model=MemberResponse,
    status_code=status.HTTP_201_CREATED
)
def add_member(
    site_id: int,
    member_data: MemberCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Tìm công trình
    site = (
        db.query(ConstructionSite)
        .filter(
            ConstructionSite.id == site_id
        )
        .first()
    )
    if site is None:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy công trình"
        )

    # Chỉ OWNER mới được thêm member
    if site.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Chỉ OWNER mới được thêm thành viên"
        )

    # Kiểm tra user cần thêm có tồn tại không
    user = (
        db.query(User)
        .filter(
            User.id == member_data.user_id
        )
        .first()
    )
    if user is None:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy user"
        )

    # Kiểm tra user đã ở trong công trình chưa
    existing_member = (
        db.query(SiteMember)
        .filter(
            SiteMember.site_id == site_id,
            SiteMember.user_id == member_data.user_id
        )
        .first()
    )
    if existing_member:
        raise HTTPException(
            status_code=400,
            detail="User đã là thành viên công trình"
        )

    # Tạo member mới
    member = SiteMember(
        site_id=site_id,
        user_id=member_data.user_id,
        role="MEMBER"
    )

    db.add(member)
    db.commit()
    db.refresh(member)

    # Ghi log thao tác thêm thành viên
    create_activity_log(
        db=db,
        user_id=current_user.id,
        site_id=site_id,
        action="ADD_MEMBER",
        description=f"Thêm user {member_data.user_id} vào công trình"
    )

    return MemberResponse(
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=member.role,
        joined_at=member.joined_at
    )


# api 7: danh sách member
# GET /construction-sites/{site_id}/members
@router.get(
    "/{site_id}/members",
    response_model=list[MemberResponse]
)
def get_members(
    site_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Kiểm tra user hiện tại có thuộc công trình không
    current_member = (
        db.query(SiteMember)
        .filter(
            SiteMember.site_id == site_id,
            SiteMember.user_id == current_user.id
        )
        .first()
    )
    if current_member is None:
        raise HTTPException(
            status_code=403,
            detail="Bạn không phải thành viên công trình"
        )

    # Lấy danh sách member
    members = (
        db.query(SiteMember)
        .filter(
            SiteMember.site_id == site_id
        )
        .all()
    )

    # Tạo dữ liệu trả về
    result = []
    for member in members:
        # Tìm user tương ứng
        user = (
            db.query(User)
            .filter(
                User.id == member.user_id
            )
            .first()
        )
        result.append(
            MemberResponse(
                user_id=user.id,
                email=user.email,
                full_name=user.full_name,
                role=member.role,
                joined_at=member.joined_at
            )
        )
    return result


# api 8: xóa member
# DELETE /construction-sites/{site_id}/members/{user_id}
@router.delete(
    "/{site_id}/members/{user_id}"
)
def remove_member(
    site_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Tìm công trình
    site = (
        db.query(ConstructionSite)
        .filter(
            ConstructionSite.id == site_id
        )
        .first()
    )
    if site is None:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy công trình"
        )

    # Chỉ OWNER mới được xóa member
    if site.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Chỉ OWNER mới được xóa thành viên"
        )

    # Không cho OWNER tự xóa chính mình
    if user_id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="Không thể xóa OWNER khỏi công trình"
        )

    # Tìm member cần xóa
    member = (
        db.query(SiteMember)
        .filter(
            SiteMember.site_id == site_id,
            SiteMember.user_id == user_id
        )
        .first()
    )
    if member is None:
        raise HTTPException(
            status_code=404,
            detail="User không phải thành viên công trình"
        )

    # Xóa member
    db.delete(member)
    db.commit()

    # Ghi log thao tác xóa thành viên
    create_activity_log(
        db=db,
        user_id=current_user.id,
        site_id=site_id,
        action="REMOVE_MEMBER",
        description=f"Xóa user {user_id} khỏi công trình"
    )

    return {
        "message": "Xóa thành viên thành công"
    }