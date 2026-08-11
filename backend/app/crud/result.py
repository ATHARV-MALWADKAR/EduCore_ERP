from datetime import datetime

from sqlalchemy.orm import Session

from app.db.models.result import Result
from app.schemas.result import ResultCreate, ResultUpdate


def list_results(db: Session, *, student_id: int | None = None) -> list[Result]:
    query = db.query(Result).order_by(Result.academic_year.desc(), Result.id.desc())
    if student_id is not None:
        query = query.filter(Result.student_id == student_id)
    return query.all()


def get_result(db: Session, result_id: int) -> Result | None:
    return db.query(Result).filter(Result.id == result_id).first()


def create_result(db: Session, result: ResultCreate) -> Result:
    values = result.model_dump()
    if values.get("grade") is None:
        ratio = values["marks_obtained"] / values["max_marks"] if values["max_marks"] else 0
        values["grade"] = "A" if ratio >= .9 else "B" if ratio >= .8 else "C" if ratio >= .7 else "D" if ratio >= .6 else "F"
    db_result = Result(**values)
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    return db_result


def update_result(db: Session, result_id: int, result_update: ResultUpdate) -> Result | None:
    db_result = get_result(db, result_id)
    if not db_result:
        return None
    for field, value in result_update.model_dump(exclude_unset=True).items():
        setattr(db_result, field, value)
    db_result.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_result)
    return db_result
