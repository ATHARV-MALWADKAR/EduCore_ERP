from datetime import date as date_type

from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.db.models import Attendance, Student


def mark_attendance(
    db: Session,
    *,
    student_id: int,
    subject_id: int,
    date: date_type,
    status: str,
) -> Attendance:
    """
    Create or update an attendance record for a given student, subject, and date.
    """
    record = (
        db.query(Attendance)
        .filter(
            Attendance.student_id == student_id,
            Attendance.subject_id == subject_id,
            Attendance.date == date,
        )
        .first()
    )
    if record is None:
        record = Attendance(
            student_id=student_id,
            subject_id=subject_id,
            date=date,
            status=status,
        )
        db.add(record)
    else:
        record.status = status

    db.commit()
    db.refresh(record)
    return record


def get_student_attendance_summary(
    db: Session,
    *,
    student_id: int,
) -> dict:
    """
    Return overall attendance summary for a student across all subjects.
    """
    total = (
        db.query(func.count(Attendance.id))
        .filter(Attendance.student_id == student_id)
        .scalar()
        or 0
    )
    present = (
        db.query(func.count(Attendance.id))
        .filter(
            Attendance.student_id == student_id,
            Attendance.status == "present",
        )
        .scalar()
        or 0
    )
    percentage = float(present) / float(total) * 100.0 if total > 0 else 0.0
    return {
        "total": int(total),
        "present": int(present),
        "percentage": round(percentage, 2),
    }


def get_attendance_report(db: Session) -> list[dict]:
    """
    Aggregate attendance per student (overall present/total/percentage).
    """
    rows = (
        db.query(
            Student.id.label("student_id"),
            Student.roll_number,
            func.count(Attendance.id).label("total"),
            func.sum(case((Attendance.status == "present", 1), else_=0)).label(
                "present"
            ),
        )
        .join(Attendance, Attendance.student_id == Student.id)
        .group_by(Student.id, Student.roll_number)
        .order_by(Student.roll_number.asc())
        .all()
    )

    report: list[dict] = []
    for r in rows:
        total = int(r.total or 0)
        present = int(r.present or 0)
        percentage = float(present) / float(total) * 100.0 if total > 0 else 0.0
        report.append(
            {
                "student_id": r.student_id,
                "roll_number": r.roll_number,
                "total": total,
                "present": present,
                "percentage": round(percentage, 2),
            }
        )
    return report

