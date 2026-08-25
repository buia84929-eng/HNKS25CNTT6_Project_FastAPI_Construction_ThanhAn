from fastapi import HTTPException

def not_found(message="Không tìm thấy dữ liệu"):
    return HTTPException(
        status_code=404,
        detail=message
    )
# Lỗi khi không tìm thấy dữ liệu

def bad_request(message="Dữ liệu không hợp lệ"):
    return HTTPException(
        status_code=400,
        detail=message
    )
# Lỗi khi dữ liệu gửi lên không hợp lệ

def forbidden(message="Bạn không có quyền thực hiện"):
    return HTTPException(
        status_code=403,
        detail=message
    )
# Lỗi khi người dùng không có quyền
