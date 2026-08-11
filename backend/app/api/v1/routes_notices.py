from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import CurrentUser, RequireAdmin, RequireFaculty
from app.crud.notice import (
    create_notice,
    get_notice,
    get_notices,
    get_notices_by_user,
    get_recent_notices,
    update_notice,
    delete_notice,
)
from app.db.session import get_db
from app.schemas.notice import NoticeCreate, NoticeRead, NoticeUpdate

router = APIRouter()


@router.get("/notices", response_model=List[NoticeRead])
def list_notices(
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> List[NoticeRead]:
    """List notices visible to the current user."""
    return get_notices_by_user(db, current_user.id, skip, limit)


@router.get("/notices/recent", response_model=List[NoticeRead])
def list_recent_notices(
    limit: int = 5,
    db: Session = Depends(get_db),
) -> List[NoticeRead]:
    """List recent notices for notifications dropdown."""
    return get_recent_notices(db, limit)


@router.post("/notices", response_model=NoticeRead)
def create_new_notice(
    notice: NoticeCreate,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
) -> NoticeRead:
    """Create a new notice (admin and faculty only)."""
    if current_user.role.name not in ["admin", "faculty"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and faculty can create notices",
        )
    payload = notice.model_dump(exclude={"created_by_id"})
    payload["created_by_id"] = current_user.id
    return create_notice(db, NoticeCreate(**payload))


@router.get("/notices/{notice_id}", response_model=NoticeRead)
def get_notice_details(
    notice_id: int,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
) -> NoticeRead:
    """Get notice details."""
    notice = get_notice(db, notice_id)
    if not notice:
        raise HTTPException(status_code=404, detail="Notice not found")
    if current_user.role.name != "admin":
        visible_ids = {item.id for item in get_notices_by_user(db, current_user.id, 0, 1000)}
        if notice.id not in visible_ids:
            raise HTTPException(status_code=403, detail="Not authorized to view this notice")
    return notice


@router.put("/notices/{notice_id}", response_model=NoticeRead)
def update_notice_details(
    notice_id: int,
    notice_update: NoticeUpdate,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
) -> NoticeRead:
    """Update notice (creator only)."""
    notice = get_notice(db, notice_id)
    if not notice or notice.created_by_id != current_user.id:
        raise HTTPException(status_code=404, detail="Notice not found or not authorized")
    updated = update_notice(db, notice_id, notice_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Notice not found")
    return updated


@router.delete("/notices/{notice_id}")
def delete_notice_item(
    notice_id: int,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    """Delete notice (creator only)."""
    notice = get_notice(db, notice_id)
    if not notice or notice.created_by_id != current_user.id:
        raise HTTPException(status_code=404, detail="Notice not found or not authorized")
    success = delete_notice(db, notice_id)
    if not success:
        raise HTTPException(status_code=404, detail="Notice not found")
    return {"message": "Notice deleted successfully"}

