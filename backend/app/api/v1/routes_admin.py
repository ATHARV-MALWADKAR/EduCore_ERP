"""
Admin/System configuration endpoints (Departments, Courses, Subjects, Users).
"""
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_active_user, RequireAdmin
from app.crud import entities as crud
from app.schemas.entities import (
    DepartmentRead, DepartmentCreate, DepartmentUpdate,
    CourseRead, CourseCreate, CourseUpdate,
    PaginatedResponse, UserRead
)
from app.db.models import User

router = APIRouter()

# ============ Sub-routers for organizational entities ============

@router.get("/departments", response_model=PaginatedResponse)
def list_departments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """List all departments (Open to all active users)."""
    depts = crud.list_departments(db, skip=skip, limit=limit, search=search)
    total = crud.count_departments(db, search=search)
    data = [DepartmentRead.model_validate(d).model_dump() for d in depts]
    return {"data": data, "meta": {"skip": skip, "limit": limit, "total": total}, "errors": []}


@router.post("/departments", response_model=DepartmentRead, status_code=status.HTTP_201_CREATED)
def create_department(
    dept_in: DepartmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequireAdmin)
) -> Any:
    """Create department (Admin only)."""
    dept = crud.create_department(db, name=dept_in.name, code=dept_in.code, description=dept_in.description)
    return dept


@router.get("/courses", response_model=PaginatedResponse)
def list_courses(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    department_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """List all courses (Open to all active users)."""
    courses = crud.list_courses(db, skip=skip, limit=limit, department_id=department_id)
    total = crud.count_courses(db, department_id=department_id)
    data = [CourseRead.model_validate(c).model_dump() for c in courses]
    return {"data": data, "meta": {"skip": skip, "limit": limit, "total": total}, "errors": []}


@router.post("/courses", response_model=CourseRead, status_code=status.HTTP_201_CREATED)
def create_course(
    course_in: CourseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequireAdmin)
) -> Any:
    """Create course (Admin only)."""
    course = crud.create_course(
        db,
        name=course_in.name,
        code=course_in.code,
        department_id=course_in.department_id,
        duration_years=course_in.duration_years
    )
    return course


@router.get("/users", response_model=PaginatedResponse)
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    role: str = None,
    search: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequireAdmin)
) -> Any:
    """List system users (Admin only)."""
    users = crud.list_users(db, skip=skip, limit=limit, role=role, search=search)
    total = crud.count_users(db, role=role, search=search)

    # Needs a bit custom serialization due to relationships
    data = []
    for u in users:
        u_dict = UserRead.model_validate(u).model_dump()
        u_dict["role"] = u.role.name
        data.append(u_dict)

    return {"data": data, "meta": {"skip": skip, "limit": limit, "total": total}, "errors": []}

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequireAdmin)
) -> None:
    """Delete user (Admin only)."""
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")

    success = crud.delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
