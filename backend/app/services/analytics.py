from datetime import datetime, timedelta

from sqlalchemy import case, func, literal_column
from sqlalchemy.orm import Session

from app.db.models.attendance import Attendance
from app.db.models.faculty import Faculty
from app.db.models.student import Student
from app.db.models.submission import Submission


def _format_date(dt: datetime) -> str:
    return dt.date().isoformat()


def get_admin_dashboard_stats(db: Session) -> dict:
    """Return dashboard analytics used on the admin dashboard."""

    total_students = db.query(func.count(Student.id)).scalar() or 0
    total_faculty = db.query(func.count(Faculty.id)).scalar() or 0

    # Attendance rate (last 30 days)
    attendance_query = db.query(
        func.count(Attendance.id).label("total"),
        func.sum(case((Attendance.status == "present", 1), else_=0)).label("present"),
    )
    attendance_totals = attendance_query.one()
    attendance_rate = 0.0
    if attendance_totals and attendance_totals.total:
        attendance_rate = (attendance_totals.present or 0) / attendance_totals.total * 100

    # Assignments pending = submissions without marks
    assignments_pending = (
        db.query(func.count(Submission.id))
        .filter(Submission.marks_given.is_(None))
        .scalar()
        or 0
    )

    # Trend data (7 days) for attendance rate and ungraded submissions
    today = datetime.utcnow().date()
    start = today - timedelta(days=6)

    attendance_trend = []
    for i in range(7):
        day = start + timedelta(days=i)
        totals = (
            db.query(
                func.count(Attendance.id).label("total"),
                func.sum(case((Attendance.status == "present", 1), else_=0)).label("present"),
            )
            .filter(Attendance.date == day)
            .one()
        )
        rate = 0.0
        if totals and totals.total:
            rate = (totals.present or 0) / totals.total * 100
        attendance_trend.append({"date": day.isoformat(), "rate": rate})

    pending_trend = []
    for i in range(7):
        day = start + timedelta(days=i)
        count = (
            db.query(func.count(Submission.id))
            .filter(func.date(Submission.created_at) == day)
            .filter(Submission.marks_given.is_(None))
            .scalar()
            or 0
        )
        pending_trend.append({"date": day.isoformat(), "pending": count})

    return {
        "total_students": total_students,
        "total_faculty": total_faculty,
        "attendance_rate": round(attendance_rate, 2),
        "assignments_pending": assignments_pending,
        "attendance_trend": attendance_trend,
        "pending_trend": pending_trend,
    }
