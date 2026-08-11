from datetime import date

from pydantic import BaseModel

from enum import Enum


class AttendanceStatus(str, Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"


class AttendanceBase(BaseModel):
    student_id: int
    subject_id: int
    date: date
    status: AttendanceStatus


class AttendanceCreate(AttendanceBase):
    pass


class AttendanceRead(AttendanceBase):
    id: int

    class Config:
        from_attributes = True

