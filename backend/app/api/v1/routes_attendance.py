"""
Attendance API endpoints.
"""
from datetime import date
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_active_user, RequireAdmin, RequireFaculty
from app.crud import entities as crud
from app.schemas.entities import (
    AttendanceRead, AttendanceCreate, AttendanceUpdate, PaginatedResponse
)
from app.db.models import User

router = APIRouter()


@router.get("/", response_model=PaginatedResponse)
def list_attendance(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    student_id: int = None,
    subject_id: int = None,
    date_from: date = None,
    date_to: date = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """List attendance records."""
    # Student can only see their own attendance
    if current_user.role.name == "student":
        student_profile = current_user.student_profile
        if not student_profile:
            raise HTTPException(status_code=400, detail="Student profile not found")
        # Override student_id filter to force their own ID
        student_id = student_profile.id

    records = crud.list_attendance(
        db, skip=skip, limit=limit,
        student_id=student_id, subject_id=subject_id,
        date_from=date_from, date_to=date_to
    )
    total = crud.count_attendance(
        db, student_id=student_id, subject_id=subject_id,
        date_from=date_from, date_to=date_to
    )

    data = [AttendanceRead.model_validate(a).model_dump() for a in records]
    return {"data": data, "meta": {"skip": skip, "limit": limit, "total": total}, "errors": []}


@router.post("/mark", response_model=AttendanceRead)
def mark_attendance(
    attendance_in: AttendanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequireFaculty)
) -> Any:
    """Mark or update attendance for a student (Faculty only)."""
    # In a real app, verify the faculty teaches this subject
    record = crud.mark_attendance(
        db,
        student_id=attendance_in.student_id,
        subject_id=attendance_in.subject_id,
        date=attendance_in.date,
        status=attendance_in.status,
        remarks=attendance_in.remarks
    )
    return record


@router.get("/summary/student/{student_id}")
def get_student_summary(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Get aggregated attendance summary for a student."""
    # Enforce permissions
    if current_user.role.name == "student":
        if not current_user.student_profile or current_user.student_profile.id != student_id:
            raise HTTPException(status_code=403, detail="Not authorized")

    summary = crud.get_student_attendance_summary(db, student_id)
    return summary


@router.get("/report/overall")
def get_overall_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(RequireAdmin)
) -> Any:
    """Get global attendance report (Admin only)."""
    return crud.get_attendance_report(db)
