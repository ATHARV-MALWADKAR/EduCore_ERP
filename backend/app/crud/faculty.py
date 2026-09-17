"""CRUD operations for Faculty model."""
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_

from app.db.models import Faculty, User


def get_faculty(db: Session, faculty_id: int) -> Optional[Faculty]:
    """Get faculty by ID."""
    return db.query(Faculty).options(
        joinedload(Faculty.user),
        joinedload(Faculty.department)
    ).filter(Faculty.id == faculty_id).first()


def get_faculty_by_user_id(db: Session, user_id: int) -> Optional[Faculty]:
    """Get faculty by user ID."""
    return db.query(Faculty).options(
        joinedload(Faculty.user),
        joinedload(Faculty.department)
    ).filter(Faculty.user_id == user_id).first()


def get_faculty_by_employee_id(db: Session, employee_id: str) -> Optional[Faculty]:
    """Get faculty by employee ID."""
    return db.query(Faculty).options(
        joinedload(Faculty.user),
        joinedload(Faculty.department)
    ).filter(Faculty.employee_id == employee_id).first()


def create_faculty(db: Session, user_id: int, employee_id: str, department_id: int, designation: Optional[str] = None) -> Faculty:
    """Create new faculty."""
    faculty = Faculty(
        user_id=user_id,
        employee_id=employee_id,
        department_id=department_id,
        designation=designation
    )
    db.add(faculty)
    db.commit()
    db.refresh(faculty)
    return faculty


def update_faculty(db: Session, faculty_id: int, employee_id: Optional[str] = None,
                   department_id: Optional[int] = None, designation: Optional[str] = None) -> Optional[Faculty]:
    """Update faculty."""
    faculty = get_faculty(db, faculty_id)
    if not faculty:
        return None

    if employee_id is not None:
        faculty.employee_id = employee_id
    if department_id is not None:
        faculty.department_id = department_id
    if designation is not None:
        faculty.designation = designation

    faculty.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(faculty)
    return faculty


def delete_faculty(db: Session, faculty_id: int) -> bool:
    """Delete faculty."""
    faculty = get_faculty(db, faculty_id)
    if not faculty:
        return False

    db.delete(faculty)
    db.commit()
    return True