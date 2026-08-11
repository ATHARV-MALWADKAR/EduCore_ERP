from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import CurrentUser
from app.crud.result import create_result, get_result, list_results, update_result
from app.db.session import get_db
from app.schemas.result import ResultCreate, ResultRead, ResultUpdate

router = APIRouter()


def _student_id_for_user(current_user, requested: int | None = None) -> int | None:
    if current_user.role.name == "student":
        if not current_user.student_profile:
            raise HTTPException(status_code=404, detail="Student profile not found")
        if requested is not None and requested != current_user.student_profile.id:
            raise HTTPException(status_code=403, detail="Not authorized")
        return current_user.student_profile.id
    return requested


@router.get("/results", response_model=list[ResultRead])
def get_results(student_id: int | None = None, current_user: CurrentUser = None, db: Session = Depends(get_db)):
    return list_results(db, student_id=_student_id_for_user(current_user, student_id))


@router.post("/results", response_model=ResultRead, status_code=status.HTTP_201_CREATED)
def add_result(result: ResultCreate, current_user: CurrentUser, db: Session = Depends(get_db)):
    if current_user.role.name not in {"admin", "faculty"}:
        raise HTTPException(status_code=403, detail="Administrator or faculty access required")
    if result.marks_obtained < 0 or result.max_marks <= 0 or result.marks_obtained > result.max_marks:
        raise HTTPException(status_code=400, detail="Marks must be between zero and the maximum marks")
    return create_result(db, result)


@router.put("/results/{result_id}", response_model=ResultRead)
def edit_result(result_id: int, result_update: ResultUpdate, current_user: CurrentUser, db: Session = Depends(get_db)):
    if current_user.role.name not in {"admin", "faculty"}:
        raise HTTPException(status_code=403, detail="Administrator or faculty access required")
    if not get_result(db, result_id):
        raise HTTPException(status_code=404, detail="Result not found")
    return update_result(db, result_id, result_update)
