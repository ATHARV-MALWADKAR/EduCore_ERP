"""
Faculty API endpoints.
"""
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_active_user, RequireAdmin
from app.crud import entities as crud
from app.schemas.entities import (
    FacultyRead, FacultyCreate, FacultyUpdate, PaginatedResponse
)
from app.db.models import User

router = APIRouter()


@router.get("/", response_model=PaginatedResponse)
def list_faculty(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    department_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """List all faculty members."""
    faculty = crud.list_faculty(db, skip=skip, limit=limit, department_id=department_id)
    total = crud.count_faculty(db, department_id=department_id)

    data = [FacultyRead.model_validate(f).model_dump() for f in faculty]
    return {"data": data, "meta": {"skip": skip, "limit": limit, "total": total}, "errors": []}


@router.get("/{faculty_id}", response_model=FacultyRead)
def get_faculty(
    faculty_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Get faculty details."""
    faculty = crud.get_faculty(db, faculty_id)
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty not found")
    return faculty


@router.post("/", response_model=FacultyRead, status_code=status.HTTP_201_CREATED)
def create_faculty(
    faculty_in: FacultyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequireAdmin)
) -> Any:
    """Create new faculty member (Admin only)."""
    user = crud.get_user(db, faculty_in.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    faculty = crud.create_faculty(
        db,
        user_id=faculty_in.user_id,
        employee_id=faculty_in.employee_id,
        department_id=faculty_in.department_id,
        designation=faculty_in.designation
    )
    return faculty


@router.patch("/{faculty_id}", response_model=FacultyRead)
def update_faculty(
    faculty_id: int,
    faculty_in: FacultyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequireAdmin)
) -> Any:
    """Update faculty details (Admin only)."""
    faculty = crud.update_faculty(
        db,
        faculty_id=faculty_id,
        employee_id=faculty_in.employee_id,
        department_id=faculty_in.department_id,
        designation=faculty_in.designation
    )
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty not found")
    return faculty


@router.delete("/{faculty_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_faculty(
    faculty_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequireAdmin)
) -> None:
    """Delete faculty member (Admin only)."""
    success = crud.delete_faculty(db, faculty_id)
    if not success:
        raise HTTPException(status_code=404, detail="Faculty not found")
