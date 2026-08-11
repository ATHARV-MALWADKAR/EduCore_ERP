from datetime import time

from pydantic import BaseModel


class TimetableEntryBase(BaseModel):
    course_id: int
    subject_id: int
    faculty_id: int
    day_of_week: int  # 1=Monday, 7=Sunday
    start_time: time
    end_time: time
    room: str | None = None
    academic_year: str


class TimetableEntryCreate(TimetableEntryBase):
    pass


class TimetableEntryRead(TimetableEntryBase):
    id: int

    class Config:
        from_attributes = True

