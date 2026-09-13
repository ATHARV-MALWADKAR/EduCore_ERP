"""Complete CRUD operations for all entities."""
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_, func

from app.db.models import (
    Role, User, Department, Course, Subject, Student, Faculty,
    Enrollment, Attendance, Assignment, Submission, Result, Notice, TimetableEntry
)


# ============ Role CRUD ============
def list_roles(db: Session, skip: int = 0, limit: int = 100) -> List[Role]:
    return db.query(Role).offset(skip).limit(limit).all()


def get_role(db: Session, role_id: int) -> Optional[Role]:
    return db.query(Role).filter(Role.id == role_id).first()


def get_role_by_name(db: Session, name: str) -> Optional[Role]:
    return db.query(Role).filter(Role.name == name).first()


def create_role(db: Session, name: str, description: Optional[str] = None) -> Role:
    role = Role(name=name, description=description)
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


def update_role(db: Session, role_id: int, name: Optional[str] = None, description: Optional[str] = None) -> Optional[Role]:
    role = get_role(db, role_id)
    if not role:
        return None
    if name:
        role.name = name
    if description is not None:
        role.description = description
    role.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(role)
    return role


def delete_role(db: Session, role_id: int) -> bool:
    role = get_role(db, role_id)
    if not role:
        return False
    db.delete(role)
    db.commit()
    return True


# ============ User CRUD ============
def list_users(db: Session, skip: int = 0, limit: int = 100, role: Optional[str] = None, search: Optional[str] = None) -> List[User]:
    query = db.query(User).options(joinedload(User.role))
    if role:
        query = query.join(Role).filter(Role.name == role)
    if search:
        query = query.filter(or_(User.email.ilike(f"%{search}%"), User.full_name.ilike(f"%{search}%")))
    return query.offset(skip).limit(limit).all()


def count_users(db: Session, role: Optional[str] = None, search: Optional[str] = None) -> int:
    query = db.query(User)
    if role:
        query = query.join(Role).filter(Role.name == role)
    if search:
        query = query.filter(or_(User.email.ilike(f"%{search}%"), User.full_name.ilike(f"%{search}%")))
    return query.count()


def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).options(joinedload(User.role)).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).options(joinedload(User.role)).filter(User.email == email).first()


def create_user(db: Session, email: str, full_name: str, hashed_password: str, role_id: int) -> User:
    user = User(email=email, full_name=full_name, hashed_password=hashed_password, role_id=role_id)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user_id: int, email: Optional[str] = None, full_name: Optional[str] = None, is_active: Optional[bool] = None) -> Optional[User]:
    user = get_user(db, user_id)
    if not user:
        return None
    if email:
        user.email = email
    if full_name:
        user.full_name = full_name
    if is_active is not None:
        user.is_active = is_active
    user.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int) -> bool:
    user = get_user(db, user_id)
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True


# ============ Department CRUD ============
def list_departments(db: Session, skip: int = 0, limit: int = 100, search: Optional[str] = None) -> List[Department]:
    query = db.query(Department)
    if search:
        query = query.filter(or_(Department.name.ilike(f"%{search}%"), Department.code.ilike(f"%{search}%")))
    return query.offset(skip).limit(limit).all()


def count_departments(db: Session, search: Optional[str] = None) -> int:
    query = db.query(Department)
    if search:
        query = query.filter(or_(Department.name.ilike(f"%{search}%"), Department.code.ilike(f"%{search}%")))
    return query.count()


def get_department(db: Session, dept_id: int) -> Optional[Department]:
    return db.query(Department).filter(Department.id == dept_id).first()


def create_department(db: Session, name: str, code: str, description: Optional[str] = None) -> Department:
    dept = Department(name=name, code=code, description=description)
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return dept


def update_department(db: Session, dept_id: int, name: Optional[str] = None, code: Optional[str] = None, description: Optional[str] = None) -> Optional[Department]:
    dept = get_department(db, dept_id)
    if not dept:
        return None
    if name:
        dept.name = name
    if code:
        dept.code = code
    if description is not None:
        dept.description = description
    dept.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(dept)
    return dept


def delete_department(db: Session, dept_id: int) -> bool:
    dept = get_department(db, dept_id)
    if not dept:
        return False
    db.delete(dept)
    db.commit()
    return True


# ============ Course CRUD ============
def list_courses(db: Session, skip: int = 0, limit: int = 100, department_id: Optional[int] = None) -> List[Course]:
    query = db.query(Course).options(joinedload(Course.department))
    if department_id:
        query = query.filter(Course.department_id == department_id)
    return query.offset(skip).limit(limit).all()


def count_courses(db: Session, department_id: Optional[int] = None) -> int:
    query = db.query(Course)
    if department_id:
        query = query.filter(Course.department_id == department_id)
    return query.count()


def get_course(db: Session, course_id: int) -> Optional[Course]:
    return db.query(Course).options(joinedload(Course.department)).filter(Course.id == course_id).first()


def create_course(db: Session, name: str, code: str, department_id: int, duration_years: int) -> Course:
    course = Course(name=name, code=code, department_id=department_id, duration_years=duration_years)
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


def update_course(db: Session, course_id: int, name: Optional[str] = None, code: Optional[str] = None, department_id: Optional[int] = None, duration_years: Optional[int] = None) -> Optional[Course]:
    course = get_course(db, course_id)
    if not course:
        return None
    if name:
        course.name = name
    if code:
        course.code = code
    if department_id:
        course.department_id = department_id
    if duration_years:
        course.duration_years = duration_years
    course.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(course)
    return course


def delete_course(db: Session, course_id: int) -> bool:
    course = get_course(db, course_id)
    if not course:
        return False
    db.delete(course)
    db.commit()
    return True


# ============ Subject CRUD ============
def list_subjects(db: Session, skip: int = 0, limit: int = 100, course_id: Optional[int] = None, semester: Optional[int] = None) -> List[Subject]:
    query = db.query(Subject).options(joinedload(Subject.course))
    if course_id:
        query = query.filter(Subject.course_id == course_id)
    if semester:
        query = query.filter(Subject.semester == semester)
    return query.offset(skip).limit(limit).all()


def count_subjects(db: Session, course_id: Optional[int] = None, semester: Optional[int] = None) -> int:
    query = db.query(Subject)
    if course_id:
        query = query.filter(Subject.course_id == course_id)
    if semester:
        query = query.filter(Subject.semester == semester)
    return query.count()


def get_subject(db: Session, subject_id: int) -> Optional[Subject]:
    return db.query(Subject).options(joinedload(Subject.course)).filter(Subject.id == subject_id).first()


def create_subject(db: Session, name: str, code: str, course_id: int, semester: int, credits: Optional[float] = None) -> Subject:
    subject = Subject(name=name, code=code, course_id=course_id, semester=semester, credits=credits)
    db.add(subject)
    db.commit()
    db.refresh(subject)
    return subject


def update_subject(db: Session, subject_id: int, name: Optional[str] = None, code: Optional[str] = None, course_id: Optional[int] = None, semester: Optional[int] = None, credits: Optional[float] = None) -> Optional[Subject]:
    subject = get_subject(db, subject_id)
    if not subject:
        return None
    if name:
        subject.name = name
    if code:
        subject.code = code
    if course_id:
        subject.course_id = course_id
    if semester:
        subject.semester = semester
    if credits is not None:
        subject.credits = credits
    subject.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(subject)
    return subject


def delete_subject(db: Session, subject_id: int) -> bool:
    subject = get_subject(db, subject_id)
    if not subject:
        return False
    db.delete(subject)
    db.commit()
    return True


# ============ Student CRUD ============
def list_students(db: Session, skip: int = 0, limit: int = 100, department_id: Optional[int] = None, course_id: Optional[int] = None, batch: Optional[str] = None) -> List[Student]:
    query = db.query(Student).options(joinedload(Student.user), joinedload(Student.department), joinedload(Student.course))
    if department_id:
        query = query.filter(Student.department_id == department_id)
    if course_id:
        query = query.filter(Student.course_id == course_id)
    if batch:
        query = query.filter(Student.batch == batch)
    return query.offset(skip).limit(limit).all()


def count_students(db: Session, department_id: Optional[int] = None, course_id: Optional[int] = None, batch: Optional[str] = None) -> int:
    query = db.query(Student)
    if department_id:
        query = query.filter(Student.department_id == department_id)
    if course_id:
        query = query.filter(Student.course_id == course_id)
    if batch:
        query = query.filter(Student.batch == batch)
    return query.count()


def get_student(db: Session, student_id: int) -> Optional[Student]:
    return db.query(Student).options(joinedload(Student.user), joinedload(Student.department), joinedload(Student.course)).filter(Student.id == student_id).first()


def get_student_by_user_id(db: Session, user_id: int) -> Optional[Student]:
    return db.query(Student).options(joinedload(Student.user), joinedload(Student.department), joinedload(Student.course)).filter(Student.user_id == user_id).first()


def create_student(db: Session, user_id: int, roll_number: str, department_id: int, course_id: int, batch: str) -> Student:
    student = Student(user_id=user_id, roll_number=roll_number, department_id=department_id, course_id=course_id, batch=batch)
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


def update_student(db: Session, student_id: int, roll_number: Optional[str] = None, department_id: Optional[int] = None, course_id: Optional[int] = None, batch: Optional[str] = None) -> Optional[Student]:
    student = get_student(db, student_id)
    if not student:
        return None
    if roll_number:
        student.roll_number = roll_number
    if department_id:
        student.department_id = department_id
    if course_id:
        student.course_id = course_id
    if batch:
        student.batch = batch
    student.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(student)
    return student


def delete_student(db: Session, student_id: int) -> bool:
    student = get_student(db, student_id)
    if not student:
        return False
    db.delete(student)
    db.commit()
    return True


# ============ Faculty CRUD ============
def list_faculty(db: Session, skip: int = 0, limit: int = 100, department_id: Optional[int] = None) -> List[Faculty]:
    query = db.query(Faculty).options(joinedload(Faculty.user), joinedload(Faculty.department))
    if department_id:
        query = query.filter(Faculty.department_id == department_id)
    return query.offset(skip).limit(limit).all()


def count_faculty(db: Session, department_id: Optional[int] = None) -> int:
    query = db.query(Faculty)
    if department_id:
        query = query.filter(Faculty.department_id == department_id)
    return query.count()


def get_faculty(db: Session, faculty_id: int) -> Optional[Faculty]:
    return db.query(Faculty).options(joinedload(Faculty.user), joinedload(Faculty.department)).filter(Faculty.id == faculty_id).first()


def get_faculty_by_user_id(db: Session, user_id: int) -> Optional[Faculty]:
    return db.query(Faculty).options(joinedload(Faculty.user), joinedload(Faculty.department)).filter(Faculty.user_id == user_id).first()


def create_faculty(db: Session, user_id: int, employee_id: str, department_id: int, designation: Optional[str] = None) -> Faculty:
    faculty = Faculty(user_id=user_id, employee_id=employee_id, department_id=department_id, designation=designation)
    db.add(faculty)
    db.commit()
    db.refresh(faculty)
    return faculty


def update_faculty(db: Session, faculty_id: int, employee_id: Optional[str] = None, department_id: Optional[int] = None, designation: Optional[str] = None) -> Optional[Faculty]:
    faculty = get_faculty(db, faculty_id)
    if not faculty:
        return None
    if employee_id:
        faculty.employee_id = employee_id
    if department_id:
        faculty.department_id = department_id
    if designation is not None:
        faculty.designation = designation
    faculty.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(faculty)
    return faculty


def delete_faculty(db: Session, faculty_id: int) -> bool:
    faculty = get_faculty(db, faculty_id)
    if not faculty:
        return False
    db.delete(faculty)
    db.commit()
    return True


# ============ Enrollment CRUD ============
def list_enrollments(db: Session, skip: int = 0, limit: int = 100, student_id: Optional[int] = None, course_id: Optional[int] = None, academic_year: Optional[str] = None) -> List[Enrollment]:
    query = db.query(Enrollment).options(joinedload(Enrollment.student), joinedload(Enrollment.course))
    if student_id:
        query = query.filter(Enrollment.student_id == student_id)
    if course_id:
        query = query.filter(Enrollment.course_id == course_id)
    if academic_year:
        query = query.filter(Enrollment.academic_year == academic_year)
    return query.offset(skip).limit(limit).all()


def count_enrollments(db: Session, student_id: Optional[int] = None, course_id: Optional[int] = None, academic_year: Optional[str] = None) -> int:
    query = db.query(Enrollment)
    if student_id:
        query = query.filter(Enrollment.student_id == student_id)
    if course_id:
        query = query.filter(Enrollment.course_id == course_id)
    if academic_year:
        query = query.filter(Enrollment.academic_year == academic_year)
    return query.count()


def get_enrollment(db: Session, enrollment_id: int) -> Optional[Enrollment]:
    return db.query(Enrollment).options(joinedload(Enrollment.student), joinedload(Enrollment.course)).filter(Enrollment.id == enrollment_id).first()


def create_enrollment(db: Session, student_id: int, course_id: int, academic_year: str, status: str = "active") -> Enrollment:
    enrollment = Enrollment(student_id=student_id, course_id=course_id, academic_year=academic_year, status=status)
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    return enrollment


def update_enrollment(db: Session, enrollment_id: int, status: Optional[str] = None) -> Optional[Enrollment]:
    enrollment = get_enrollment(db, enrollment_id)
    if not enrollment:
        return None
    if status:
        enrollment.status = status
    enrollment.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(enrollment)
    return enrollment


def delete_enrollment(db: Session, enrollment_id: int) -> bool:
    enrollment = get_enrollment(db, enrollment_id)
    if not enrollment:
        return False
    db.delete(enrollment)
    db.commit()
    return True


# ============ Notice CRUD ============
def list_notices(db: Session, skip: int = 0, limit: int = 100, target_audience: Optional[str] = None, department_id: Optional[int] = None) -> List[Notice]:
    query = db.query(Notice).options(joinedload(Notice.created_by)).order_by(Notice.created_at.desc())
    if target_audience:
        query = query.filter(or_(Notice.target_audience == "all", Notice.target_audience == target_audience))
    if department_id:
        query = query.filter(or_(Notice.department_id == None, Notice.department_id == department_id))
    return query.offset(skip).limit(limit).all()


def count_notices(db: Session, target_audience: Optional[str] = None, department_id: Optional[int] = None) -> int:
    query = db.query(Notice)
    if target_audience:
        query = query.filter(or_(Notice.target_audience == "all", Notice.target_audience == target_audience))
    if department_id:
        query = query.filter(or_(Notice.department_id == None, Notice.department_id == department_id))
    return query.count()


def get_notice(db: Session, notice_id: int) -> Optional[Notice]:
    return db.query(Notice).options(joinedload(Notice.created_by)).filter(Notice.id == notice_id).first()


def create_notice(db: Session, title: str, content: str, created_by_id: int, target_audience: str = "all", department_id: Optional[int] = None) -> Notice:
    notice = Notice(title=title, content=content, created_by_id=created_by_id, target_audience=target_audience, department_id=department_id)
    db.add(notice)
    db.commit()
    db.refresh(notice)
    return notice


def update_notice(db: Session, notice_id: int, title: Optional[str] = None, content: Optional[str] = None, target_audience: Optional[str] = None, department_id: Optional[int] = None) -> Optional[Notice]:
    notice = get_notice(db, notice_id)
    if not notice:
        return None
    if title:
        notice.title = title
    if content:
        notice.content = content
    if target_audience:
        notice.target_audience = target_audience
    if department_id is not None:
        notice.department_id = department_id
    notice.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(notice)
    return notice


def delete_notice(db: Session, notice_id: int) -> bool:
    notice = get_notice(db, notice_id)
    if not notice:
        return False
    db.delete(notice)
    db.commit()
    return True
