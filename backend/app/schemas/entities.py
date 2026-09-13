"""Pydantic schemas for all entity CRUD operations."""
from datetime import date, datetime, time
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field


# ============ Common Schemas ============
class PaginatedResponse(BaseModel):
    """Paginated list response."""
    data: List[dict]
    meta: dict
    errors: List[str] = []


# ============ User Schemas ============
class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    role_name: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    is_active: Optional[bool] = None


class UserRead(UserBase):
    id: int
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Role Schemas ============
class RoleBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    description: Optional[str] = Field(None, max_length=255)


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    description: Optional[str] = Field(None, max_length=255)


class RoleRead(RoleBase):
    id: int

    class Config:
        from_attributes = True


# ============ Department Schemas ============
class DepartmentBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    code: str = Field(..., min_length=2, max_length=20)
    description: Optional[str] = None


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    code: Optional[str] = Field(None, min_length=2, max_length=20)
    description: Optional[str] = None


class DepartmentRead(DepartmentBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Course Schemas ============
class CourseBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    code: str = Field(..., min_length=2, max_length=30)
    department_id: int
    duration_years: int = Field(..., ge=1, le=10)


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=150)
    code: Optional[str] = Field(None, min_length=2, max_length=30)
    department_id: Optional[int] = None
    duration_years: Optional[int] = Field(None, ge=1, le=10)


class CourseRead(CourseBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Subject Schemas ============
class SubjectBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    code: str = Field(..., min_length=2, max_length=30)
    course_id: int
    semester: int = Field(..., ge=1, le=12)
    credits: Optional[Decimal] = Field(None, ge=0, le=10)


class SubjectCreate(SubjectBase):
    pass


class SubjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=150)
    code: Optional[str] = Field(None, min_length=2, max_length=30)
    course_id: Optional[int] = None
    semester: Optional[int] = Field(None, ge=1, le=12)
    credits: Optional[Decimal] = Field(None, ge=0, le=10)


class SubjectRead(SubjectBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Student Schemas ============
class StudentBase(BaseModel):
    roll_number: str = Field(..., min_length=1, max_length=50)
    department_id: int
    course_id: int
    batch: str = Field(..., min_length=1, max_length=20)


class StudentCreate(StudentBase):
    user_id: int


class StudentUpdate(BaseModel):
    roll_number: Optional[str] = Field(None, min_length=1, max_length=50)
    department_id: Optional[int] = None
    course_id: Optional[int] = None
    batch: Optional[str] = Field(None, min_length=1, max_length=20)


class StudentRead(StudentBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Faculty Schemas ============
class FacultyBase(BaseModel):
    employee_id: str = Field(..., min_length=1, max_length=50)
    department_id: int
    designation: Optional[str] = Field(None, max_length=100)


class FacultyCreate(FacultyBase):
    user_id: int


class FacultyUpdate(BaseModel):
    employee_id: Optional[str] = Field(None, min_length=1, max_length=50)
    department_id: Optional[int] = None
    designation: Optional[str] = Field(None, max_length=100)


class FacultyRead(FacultyBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Enrollment Schemas ============
class EnrollmentBase(BaseModel):
    student_id: int
    course_id: int
    academic_year: str = Field(..., min_length=4, max_length=20)
    status: str = Field("active", pattern="^(active|dropped|completed)$")


class EnrollmentCreate(EnrollmentBase):
    pass


class EnrollmentUpdate(BaseModel):
    status: Optional[str] = Field(None, pattern="^(active|dropped|completed)$")


class EnrollmentRead(EnrollmentBase):
    id: int
    enrolled_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Attendance Schemas ============
class AttendanceBase(BaseModel):
    student_id: int
    subject_id: int
    date: date
    status: str = Field(..., pattern="^(present|absent|late)$")
    remarks: Optional[str] = Field(None, max_length=255)


class AttendanceCreate(AttendanceBase):
    pass


class AttendanceUpdate(BaseModel):
    status: Optional[str] = Field(None, pattern="^(present|absent|late)$")
    remarks: Optional[str] = Field(None, max_length=255)


class AttendanceRead(AttendanceBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Assignment Schemas ============
class AssignmentBase(BaseModel):
    subject_id: int
    title: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    due_at: datetime
    status: str = Field("draft", pattern="^(draft|published|closed)$")


class AssignmentCreate(AssignmentBase):
    pass


class AssignmentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = None
    due_at: Optional[datetime] = None
    status: Optional[str] = Field(None, pattern="^(draft|published|closed)$")


class AssignmentRead(AssignmentBase):
    id: int
    created_by_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Submission Schemas ============
class SubmissionBase(BaseModel):
    assignment_id: int
    student_id: int
    content: Optional[str] = None
    file_path: Optional[str] = Field(None, max_length=500)


class SubmissionCreate(SubmissionBase):
    pass


class SubmissionUpdate(BaseModel):
    content: Optional[str] = None
    file_path: Optional[str] = Field(None, max_length=500)


class SubmissionGrade(BaseModel):
    marks_given: Optional[Decimal] = Field(None, ge=0, le=100)
    feedback: Optional[str] = None


class SubmissionRead(SubmissionBase):
    id: int
    submitted_at: datetime
    marks_given: Optional[Decimal]
    feedback: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Result Schemas ============
class ResultBase(BaseModel):
    student_id: int
    subject_id: int
    exam_type: str = Field(..., pattern="^(mid_term|final|internal)$")
    academic_year: str
    marks_obtained: Decimal = Field(..., ge=0)
    max_marks: Decimal = Field(..., ge=1)
    grade: Optional[str] = Field(None, max_length=10)


class ResultCreate(ResultBase):
    pass


class ResultUpdate(BaseModel):
    marks_obtained: Optional[Decimal] = Field(None, ge=0)
    max_marks: Optional[Decimal] = Field(None, ge=1)
    grade: Optional[str] = Field(None, max_length=10)


class ResultRead(ResultBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Notice Schemas ============
class NoticeBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    content: str
    target_audience: str = Field("all", pattern="^(all|students|faculty)$")
    department_id: Optional[int] = None


class NoticeCreate(NoticeBase):
    pass


class NoticeUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=255)
    content: Optional[str] = None
    target_audience: Optional[str] = Field(None, pattern="^(all|students|faculty)$")
    department_id: Optional[int] = None


class NoticeRead(NoticeBase):
    id: int
    created_by_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Timetable Schemas ============
class TimetableBase(BaseModel):
    course_id: int
    subject_id: int
    faculty_id: int
    day_of_week: int = Field(..., ge=1, le=7)
    start_time: time
    end_time: time
    room: Optional[str] = Field(None, max_length=50)
    academic_year: str


class TimetableCreate(TimetableBase):
    pass


class TimetableUpdate(BaseModel):
    course_id: Optional[int] = None
    subject_id: Optional[int] = None
    faculty_id: Optional[int] = None
    day_of_week: Optional[int] = Field(None, ge=1, le=7)
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    room: Optional[str] = Field(None, max_length=50)
    academic_year: Optional[str] = None


class TimetableRead(TimetableBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
