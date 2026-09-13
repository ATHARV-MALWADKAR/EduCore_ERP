"""
Student API endpoints.
"""
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_active_user, RequireAdmin, RequireStudent, RequireFaculty
from app.crud import entities as crud
from app.schemas.entities import (
    StudentRead, StudentCreate, StudentUpdate, PaginatedResponse,
    CourseRead, ResultRead, AttendanceRead
)
from app.db.models import User

router = APIRouter()


@router.get("/", response_model=PaginatedResponse)
def list_students(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    department_id: int = None,
    course_id: int = None,
    batch: str = None,
    db: Session = Depends(get_db),
    # Only Admin and Faculty can list all students
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """List all students."""
    if current_user.role.name == "student":
        raise HTTPException(status_code=403, detail="Not authorized to list students")

    students = crud.list_students(db, skip=skip, limit=limit, department_id=department_id, course_id=course_id, batch=batch)
    total = crud.count_students(db, department_id=department_id, course_id=course_id, batch=batch)

    # Format response
    data = [StudentRead.model_validate(s).model_dump() for s in students]
    return {"data": data, "meta": {"skip": skip, "limit": limit, "total": total}, "errors": []}


@router.get("/{student_id}", response_model=StudentRead)
def get_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Get student details."""
    student = crud.get_student(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Students can only view their own profile
    if current_user.role.name == "student" and student.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this student")

    return student


@router.post("/", response_model=StudentRead, status_code=status.HTTP_201_CREATED)
def create_student(
    student_in: StudentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequireAdmin)
) -> Any:
    """Create new student (Admin only)."""
    # Ensure user exists for this student
    user = crud.get_user(db, student_in.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    student = crud.create_student(
        db,
        user_id=student_in.user_id,
        roll_number=student_in.roll_number,
        department_id=student_in.department_id,
        course_id=student_in.course_id,
        batch=student_in.batch
    )
    return student


@router.patch("/{student_id}", response_model=StudentRead)
def update_student(
    student_id: int,
    student_in: StudentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequireAdmin)
) -> Any:
    """Update student details (Admin only)."""
    student = crud.update_student(
        db,
        student_id=student_id,
        roll_number=student_in.roll_number,
        department_id=student_in.department_id,
        course_id=student_in.course_id,
        batch=student_in.batch
    )
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequireAdmin)
) -> None:
    """Delete a student (Admin only)."""
    deleted = crud.delete_student(db, student_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Student not found")
    success = crud.delete_student(db, student_id)
    if not success:
        raise HTTPException(status_code=404, detail="Student not found")
    return None


@router.get("/{student_id}/results", response_model=PaginatedResponse)
def get_student_results(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Get all results for a student."""
    student = crud.get_student(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Student can only view own results
    if current_user.role.name == "student" and student.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    results = crud.list_results(db, student_id=student_id)
    data = [ResultRead.model_validate(r).model_dump() for r in results]

    return {"data": data, "meta": {"total": len(results)}, "errors": []}
