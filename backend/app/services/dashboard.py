from datetime import datetime, timedelta
from typing import List, Dict, Any

from sqlalchemy import func, and_, or_
from sqlalchemy.orm import Session

from app.db.models.assignment import Assignment
from app.db.models.attendance import Attendance
from app.db.models.enrollment import Enrollment
from app.db.models.faculty import Faculty
from app.db.models.notice import Notice
from app.db.models.student import Student
from app.db.models.subject import Subject
from app.db.models.submission import Submission
from app.db.models.timetable import TimetableEntry
from app.db.models.user import User


def get_student_dashboard_data(db: Session, student_id: int) -> Dict[str, Any]:
    """Get dashboard data for a student."""

    # Get student info
    student = db.query(Student).filter(Student.user_id == student_id).first()
    if not student:
        return {}

    # Attendance rate (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    attendance_records = db.query(Attendance).filter(
        and_(
            Attendance.student_id == student.id,
            Attendance.date >= thirty_days_ago.date()
        )
    ).all()

    total_classes = len(attendance_records)
    present_count = sum(1 for a in attendance_records if a.status == "present")
    attendance_rate = (present_count / total_classes * 100) if total_classes > 0 else 0.0

    # Assignments due (next 7 days)
    week_from_now = datetime.utcnow() + timedelta(days=7)
    assignments_due = db.query(Assignment).filter(
        and_(
            Assignment.due_at <= week_from_now,
            Assignment.due_at >= datetime.utcnow()
        )
    ).join(Subject, Subject.id == Assignment.subject_id).join(Enrollment, Enrollment.course_id == Subject.course_id).filter(
        Enrollment.student_id == student.id
    ).count()

    # Today's schedule
    today = datetime.utcnow().date()
    day_of_week = datetime.utcnow().weekday() + 1  # Monday=1, Sunday=7
    todays_schedule = db.query(TimetableEntry).filter(
        TimetableEntry.day_of_week == day_of_week
    ).join(Enrollment, Enrollment.course_id == TimetableEntry.course_id).filter(
        Enrollment.student_id == student.id
    ).join(Subject, Subject.id == TimetableEntry.subject_id).join(
        Faculty, Faculty.id == TimetableEntry.faculty_id
    ).join(User, User.id == Faculty.user_id).all()

    todays_schedule_data = []
    for t in todays_schedule:
        todays_schedule_data.append({
            "subject_name": t.subject.name,
            "start_time": t.start_time.strftime("%I:%M %p"),
            "end_time": t.end_time.strftime("%I:%M %p"),
            "room": t.room,
            "faculty_name": t.faculty.user.full_name
        })

    # Next lecture (first upcoming today)
    next_lecture = None
    current_time = datetime.utcnow().time()
    for t in sorted(todays_schedule, key=lambda x: x.start_time):
        if t.start_time > current_time:
            next_lecture = {
                "subject_name": t.subject.name,
                "start_time": t.start_time.strftime("%I:%M %p")
            }
            break

    # Pending assignments
    pending_assignments = db.query(Assignment).filter(
        Assignment.due_at >= datetime.utcnow()
    ).join(Subject, Subject.id == Assignment.subject_id).join(Enrollment, Enrollment.course_id == Subject.course_id).filter(
        Enrollment.student_id == student.id
    ).outerjoin(Submission, and_(
        Submission.assignment_id == Assignment.id,
        Submission.student_id == student.id
    )).filter(Submission.id.is_(None)).all()

    pending_assignments_data = []
    for assignment in pending_assignments:
        pending_assignments_data.append({
            "title": assignment.title,
            "subject_name": assignment.subject.name,
            "due_date": assignment.due_at.strftime("%b %d, %Y")
        })

    # Recent notices (last 5)
    recent_notices = db.query(Notice).order_by(Notice.created_at.desc()).limit(5).all()
    recent_notices_data = []
    for notice in recent_notices:
        recent_notices_data.append({
            "title": notice.title,
            "content": notice.content,
            "created_at": notice.created_at.strftime("%b %d, %Y")
        })

    return {
        "attendance_rate": attendance_rate,
        "assignments_due": assignments_due,
        "next_lecture": next_lecture,
        "todays_schedule": todays_schedule_data,
        "pending_assignments": pending_assignments_data,
        "recent_notices": recent_notices_data
    }


def get_faculty_dashboard_data(db: Session, faculty_id: int) -> Dict[str, Any]:
    """Get dashboard data for a faculty member."""

    faculty = db.query(Faculty).filter(Faculty.user_id == faculty_id).first()
    if not faculty:
        return {}

    # Today's classes
    today = datetime.utcnow().date()
    day_of_week = datetime.utcnow().weekday() + 1  # Monday=1, Sunday=7
    todays_classes = db.query(TimetableEntry).filter(
        and_(
            TimetableEntry.faculty_id == faculty.id,
            TimetableEntry.day_of_week == day_of_week
        )
    ).count()

    # Pending evaluations (submissions without marks)
    pending_evaluations = db.query(func.count(Submission.id)).filter(
        and_(
            Assignment.created_by_id == faculty.id,
            Submission.marks_given.is_(None)
        )
    ).join(Assignment, Assignment.id == Submission.assignment_id)
    ).scalar() or 0

    # New submissions (last 24 hours)
    yesterday = datetime.utcnow() - timedelta(days=1)
    new_submissions = db.query(func.count(Submission.id)).filter(
        and_(
            Assignment.created_by_id == faculty.id,
            Submission.submitted_at >= yesterday
        )
    ).join(Assignment, Assignment.id == Submission.assignment_id)
    ).scalar() or 0

    # Today's schedule
    todays_schedule = db.query(TimetableEntry).filter(
        and_(
            TimetableEntry.faculty_id == faculty.id,
            TimetableEntry.day_of_week == day_of_week
        )
    ).join(Subject, Subject.id == TimetableEntry.subject_id).all()

    todays_schedule_data = []
    for t in todays_schedule:
        todays_schedule_data.append({
            "subject_name": t.subject.name,
            "start_time": t.start_time.strftime("%I:%M %p"),
            "end_time": t.end_time.strftime("%I:%M %p"),
            "room": t.room
        })

    # Recent submissions (last 5)
    recent_submissions = db.query(Submission).join(Assignment, Assignment.id == Submission.assignment_id).filter(
        Assignment.created_by_id == faculty.id
    ).join(
        Student, Student.id == Submission.student_id
    ).join(User, User.id == Student.user_id).order_by(
        Submission.submitted_at.desc()
    ).limit(5).all()

    recent_submissions_data = []
    for sub in recent_submissions:
        recent_submissions_data.append({
            "assignment_title": sub.assignment.title,
            "student_name": sub.student.user.full_name,
            "submitted_at": sub.submitted_at.strftime("%b %d, %Y %I:%M %p")
        })

    return {
        "todays_classes": todays_classes,
        "pending_evaluations": pending_evaluations,
        "new_submissions": new_submissions,
        "todays_schedule": todays_schedule_data,
        "recent_submissions": recent_submissions_data
    }
