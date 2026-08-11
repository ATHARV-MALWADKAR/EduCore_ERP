from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import CurrentUser, RequireAdmin, RequireFaculty, RequireStudent
from app.crud.timetable import (
    create_timetable_entry,
    delete_timetable_entry,
    get_timetable_entry,
    get_timetable_for_course,
    get_timetable_for_faculty,
    update_timetable_entry,
)
from app.db.session import get_db
from app.schemas.timetable import TimetableEntryCreate, TimetableEntryRead, TimetableEntryBase

router = APIRouter()


@router.get("/timetable", response_model=List[TimetableEntryRead])
def list_timetable(
    current_user: CurrentUser,
    course_id: int | None = None,
    db: Session = Depends(get_db),
) -> List[TimetableEntryRead]:
    """Get timetable for current user.

    - Students: see timetable for their course.
    - Faculty: see their teaching schedule.
    - Admin: may provide course_id to retrieve timetable.
    """
    role = current_user.role.name if current_user.role else None

    if role == "student":
        if not current_user.student_profile:
            raise HTTPException(status_code=404, detail="Student profile not found")
        return get_timetable_for_course(db, current_user.student_profile.course_id)

    if role == "faculty":
        if not current_user.faculty_profile:
            raise HTTPException(status_code=404, detail="Faculty profile not found")
        return get_timetable_for_faculty(db, current_user.faculty_profile.id)

    # Admin can filter by course
    if role == "admin":
        if not course_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="course_id required for admin",
            )
        return get_timetable_for_course(db, course_id)

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Not authorized",
    )


@router.post("/timetable", response_model=TimetableEntryRead)
def create_timetable(
    entry: TimetableEntryCreate,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
) -> TimetableEntryRead:
    """Create a timetable entry (admin/faculty only)."""
    if current_user.role.name not in ["admin", "faculty"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized",
        )
    if current_user.role.name == "faculty":
        if not current_user.faculty_profile:
            raise HTTPException(status_code=409, detail="Faculty profile not found")
        entry = entry.model_copy(update={"faculty_id": current_user.faculty_profile.id})
    return create_timetable_entry(db, entry)


@router.get("/timetable/{entry_id}", response_model=TimetableEntryRead)
def get_timetable_entry_details(
    entry_id: int,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
) -> TimetableEntryRead:
    entry = get_timetable_entry(db, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Timetable entry not found")
    return entry


@router.put("/timetable/{entry_id}", response_model=TimetableEntryRead)
def update_timetable_entry_route(
    entry_id: int,
    entry_update: TimetableEntryBase,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
) -> TimetableEntryRead:
    """Update timetable entry (admin/faculty only)."""
    if current_user.role.name not in ["admin", "faculty"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized",
        )
    existing = get_timetable_entry(db, entry_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Timetable entry not found")
    if current_user.role.name == "faculty":
        if not current_user.faculty_profile or existing.faculty_id != current_user.faculty_profile.id:
            raise HTTPException(status_code=403, detail="Not authorized")
        entry_update = entry_update.model_copy(update={"faculty_id": current_user.faculty_profile.id})
    updated = update_timetable_entry(db, entry_id, entry_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Timetable entry not found")
    return updated


@router.delete("/timetable/{entry_id}")
def delete_timetable_entry_route(
    entry_id: int,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    """Delete timetable entry (admin only)."""
    if current_user.role.name != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized",
        )
    success = delete_timetable_entry(db, entry_id)
    if not success:
        raise HTTPException(status_code=404, detail="Timetable entry not found")
    return {"message": "Deleted"}

