from datetime import datetime

from pydantic import BaseModel


class SubmissionBase(BaseModel):
    assignment_id: int
    student_id: int
    content: str | None = None
    marks_given: float | None = None
    feedback: str | None = None


class SubmissionCreate(BaseModel):
    assignment_id: int
    student_id: int
    content: str | None = None


class SubmissionRead(SubmissionBase):
    id: int
    submitted_at: datetime
    file_path: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SubmissionUpdate(BaseModel):
    marks_given: float | None = None
    feedback: str | None = None
