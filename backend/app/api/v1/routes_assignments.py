from pathlib import Path
from uuid import uuid4
from typing import List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.deps import CurrentUser, RequireFaculty, RequireStudent
from app.crud.assignment import (
    create_assignment,
    get_assignment,
    get_assignments_by_faculty,
    get_assignments_by_subject,
    update_assignment,
)
from app.crud.submission import (
    create_submission,
    get_submission,
    get_submission_by_student_assignment,
    get_submissions_by_assignment,
    update_submission,
)
from app.db.session import get_db
from app.schemas.assignment import AssignmentCreate, AssignmentRead, AssignmentUpdate
from app.schemas.submission import SubmissionCreate, SubmissionRead, SubmissionUpdate

router = APIRouter()

UPLOAD_DIR = Path("uploads") / "assignments"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.get("/assignments", response_model=List[AssignmentRead])
def list_assignments(
    subject_id: int | None = None,
    current_user: CurrentUser = None,
    db: Session = Depends(get_db),
) -> List[AssignmentRead]:
    """List assignments. Faculty see their own, students see by subject."""
    if current_user.role.name == "faculty":
        assignments = get_assignments_by_faculty(db, current_user.faculty_profile.id)
    else:
        if not subject_id:
            raise HTTPException(status_code=400, detail="subject_id required for students")
        assignments = get_assignments_by_subject(db, subject_id)
    return assignments


@router.post("/assignments", response_model=AssignmentRead)
def create_new_assignment(
    assignment: AssignmentCreate,
    current_user: RequireFaculty,
    db: Session = Depends(get_db),
) -> AssignmentRead:
    """Create a new assignment (faculty only)."""
    if not current_user.faculty_profile:
        raise HTTPException(status_code=409, detail="Faculty profile is required before creating assignments")
    payload = assignment.model_dump(exclude={"created_by_id"})
    payload["created_by_id"] = current_user.faculty_profile.id
    return create_assignment(db, AssignmentCreate(**payload))


@router.get("/assignments/{assignment_id}", response_model=AssignmentRead)
def get_assignment_details(
    assignment_id: int,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
) -> AssignmentRead:
    """Get assignment details."""
    assignment = get_assignment(db, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    # Check permissions: faculty can see their own, students can see published assignments
    if current_user.role.name == "faculty" and assignment.created_by_id != current_user.faculty_profile.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return assignment


@router.put("/assignments/{assignment_id}", response_model=AssignmentRead)
def update_assignment_details(
    assignment_id: int,
    assignment_update: AssignmentUpdate,
    current_user: RequireFaculty,
    db: Session = Depends(get_db),
) -> AssignmentRead:
    """Update assignment (faculty only)."""
    assignment = get_assignment(db, assignment_id)
    if not assignment or assignment.created_by_id != current_user.faculty_profile.id:
        raise HTTPException(status_code=404, detail="Assignment not found or not authorized")
    updated = update_assignment(db, assignment_id, assignment_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return updated


@router.post("/assignments/{assignment_id}/submit", response_model=SubmissionRead)
def submit_assignment(
    assignment_id: int,
    current_user: RequireStudent,
    content: str | None = Form(None),
    file: UploadFile | None = File(None),
    db: Session = Depends(get_db),
) -> SubmissionRead:
    """Submit assignment (students only)."""
    assignment = get_assignment(db, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # Check if already submitted
    existing = get_submission_by_student_assignment(db, current_user.student_profile.id, assignment_id)
    if existing:
        raise HTTPException(status_code=400, detail="Already submitted")
    
    file_path = None
    if file:
        suffix = Path(file.filename or "submission").suffix.lower()
        if suffix not in {".pdf", ".doc", ".docx", ".txt", ".zip"}:
            raise HTTPException(status_code=400, detail="Unsupported file type")
        target = UPLOAD_DIR / f"{assignment_id}_{current_user.student_profile.id}_{uuid4().hex}{suffix}"
        size = 0
        with target.open("wb") as buffer:
            while chunk := file.file.read(1024 * 1024):
                size += len(chunk)
                if size > settings.max_upload_size_mb * 1024 * 1024:
                    buffer.close()
                    target.unlink(missing_ok=True)
                    raise HTTPException(status_code=413, detail="Uploaded file is too large")
                buffer.write(chunk)
        file_path = str(target)

    submission = SubmissionCreate(
        assignment_id=assignment_id,
        student_id=current_user.student_profile.id,
        content=content,
    )
    return create_submission(db, submission, file_path)


@router.get("/assignments/{assignment_id}/submissions", response_model=List[SubmissionRead])
def list_submissions(
    assignment_id: int,
    current_user: RequireFaculty,
    db: Session = Depends(get_db),
) -> List[SubmissionRead]:
    """List submissions for an assignment (faculty only)."""
    assignment = get_assignment(db, assignment_id)
    if not assignment or assignment.created_by_id != current_user.faculty_profile.id:
        raise HTTPException(status_code=404, detail="Assignment not found or not authorized")
    return get_submissions_by_assignment(db, assignment_id)


@router.put("/submissions/{submission_id}/grade", response_model=SubmissionRead)
def grade_submission(
    submission_id: int,
    submission_update: SubmissionUpdate,
    current_user: RequireFaculty,
    db: Session = Depends(get_db),
) -> SubmissionRead:
    """Grade a submission (faculty only)."""
    submission = get_submission(db, submission_id)
    if not submission or submission.assignment.created_by_id != current_user.faculty_profile.id:
        raise HTTPException(status_code=404, detail="Submission not found or not authorized")
    updated = update_submission(db, submission_id, submission_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Submission not found")
    return updated

