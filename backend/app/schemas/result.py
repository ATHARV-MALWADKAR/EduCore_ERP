from pydantic import BaseModel


class ResultBase(BaseModel):
    student_id: int
    subject_id: int
    exam_type: str
    academic_year: str
    marks_obtained: float
    max_marks: float
    grade: str | None = None


class ResultCreate(ResultBase):
    pass


class ResultRead(ResultBase):
    id: int

    class Config:
        from_attributes = True


class ResultUpdate(BaseModel):
    marks_obtained: float | None = None
    max_marks: float | None = None
    grade: str | None = None

