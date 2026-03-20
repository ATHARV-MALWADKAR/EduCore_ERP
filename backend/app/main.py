from datetime import date

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from app.db.base import Base
from app.db.session import engine, get_db, SessionLocal
from app.db.init_db import seed_database
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
from fastapi import Form
from pathlib import Path

from app.core.config import settings
from app.core.deps import CurrentUser, RequireAdmin, RequireFaculty, RequireStudent
from app.core.logging import configure_logging
from app.core.middleware import AuthMiddleware, ErrorHandlerMiddleware, RateLimitMiddleware, SecureHeadersMiddleware
from app.crud import attendance as attendance_crud
from app.crud import student as student_crud
from sqlalchemy.orm import Session
from app.api.v1.routes_auth import router as auth_router
from app.api.v1.routes_students import router as students_router
from app.api.v1.routes_faculty import router as faculty_router
from app.api.v1.routes_admin import router as admin_router
from app.api.v1.routes_attendance import router as attendance_router
from app.api.v1.routes_assignments import router as assignments_router
from app.api.v1.routes_results import router as results_router
from app.api.v1.routes_notices import router as notices_router
from app.api.v1.routes_timetable import router as timetable_router

from fastapi.staticfiles import StaticFiles

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "app/templates"))

configure_logging()

app = FastAPI(
    title="College ERP API",
    version="0.1.0",
    description="Backend API for the College ERP system.",
)

Base.metadata.create_all(bind=engine)

# Seed database on startup
@app.on_event("startup")
def startup_event():
    """Initialize database with seed data on startup."""
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()

# Mount static files
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "app/static")), name="static")

app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(RateLimitMiddleware, max_requests=200, window_seconds=60)
app.add_middleware(SecureHeadersMiddleware)
app.add_middleware(AuthMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["health"])
def health_check() -> dict:
    return {"status": "ok"}


api_prefix = "/api/v1"

app.include_router(auth_router, prefix=api_prefix, tags=["auth"])
app.include_router(students_router, prefix=api_prefix, tags=["students"])
app.include_router(faculty_router, prefix=api_prefix, tags=["faculty"])
app.include_router(admin_router, prefix=api_prefix, tags=["admin"])
app.include_router(attendance_router, prefix=api_prefix, tags=["attendance"])
app.include_router(assignments_router, prefix=api_prefix, tags=["assignments"])
app.include_router(results_router, prefix=api_prefix, tags=["results"])
app.include_router(notices_router, prefix=api_prefix, tags=["notices"])
app.include_router(timetable_router, prefix=api_prefix, tags=["timetable"])


# ------------------ Login UI Route ------------------

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {"request": request}
    )


# ------------------ Dashboard UI Route ------------------

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request}
    )

@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request,
    current_user: RequireAdmin,
):
    return templates.TemplateResponse(
        "admin_dashboard.html",
        {"request": request, "current_user": current_user}
    )


@app.get("/faculty", response_class=HTMLResponse)
async def faculty_dashboard(
    request: Request,
    current_user: RequireFaculty,
):
    return templates.TemplateResponse(
        "faculty_dashboard.html",
        {"request": request, "current_user": current_user}
    )


@app.get("/student", response_class=HTMLResponse)
async def student_dashboard(
    request: Request,
    current_user: RequireStudent,
):
    return templates.TemplateResponse(
        "student_dashboard.html",
        {"request": request, "current_user": current_user}
    )

    


@app.get("/students", response_class=HTMLResponse)
async def students_page(
    request: Request,
    db: Session = Depends(get_db),
):
    students = student_crud.list_students(db)
    return templates.TemplateResponse(
        "students.html",
        {
            "request": request,
            "students": students,
        },
    )


@app.post("/students/add")
async def add_student(
    request: Request,
    user_id: int = Form(...),
    roll_number: str = Form(...),
    department_id: int = Form(...),
    course_id: int = Form(...),
    batch: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        student_crud.create_student(
            db,
            user_id=user_id,
            roll_number=roll_number,
            department_id=department_id,
            course_id=course_id,
            batch=batch,
        )
    except Exception as exc:  # simple catch; can be refined
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not create student: {exc}",
        ) from exc

    return RedirectResponse(url="/students", status_code=status.HTTP_303_SEE_OTHER)


@app.post("/students/{student_id}/delete")
async def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
):
    success = student_crud.delete_student(db, student_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )
    return RedirectResponse(url="/students", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/attendance", response_class=HTMLResponse)
async def attendance_page(
    request: Request,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    role = current_user.role.name if current_user.role else None

    student_summary = None
    if role == "student" and current_user.student_profile:
        student_summary = attendance_crud.get_student_attendance_summary(
            db, student_id=current_user.student_profile.id
        )

    report = None
    if role == "admin":
        report = attendance_crud.get_attendance_report(db)

    return templates.TemplateResponse(
        "attendance.html",
        {
            "request": request,
            "current_role": role,
            "student_summary": student_summary,
            "attendance_report": report,
        },
    )


@app.post("/attendance/mark")
async def mark_attendance(
    current_user: RequireFaculty,
    student_id: int = Form(...),
    subject_id: int = Form(...),
    status_value: str = Form(..., alias="status"),
    date_value: date = Form(default_factory=date.today, alias="date"),
    db: Session = Depends(get_db),
):
    if status_value not in {"present", "absent"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status; must be 'present' or 'absent'",
        )

    attendance_crud.mark_attendance(
        db,
        student_id=student_id,
        subject_id=subject_id,
        date=date_value,
        status=status_value,
    )
    return RedirectResponse(url="/attendance", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/attendance/report", response_class=HTMLResponse)
async def attendance_report(
    request: Request,
    current_user: RequireAdmin,
    db: Session = Depends(get_db),
):
    report = attendance_crud.get_attendance_report(db)
    return templates.TemplateResponse(
        "attendance.html",
        {
            "request": request,
            "current_role": current_user.role.name if current_user.role else None,
            "student_summary": None,
            "attendance_report": report,
        },
    )


@app.get("/faculty-module", response_class=HTMLResponse)
async def faculty_page(request: Request):
    return templates.TemplateResponse("faculty.html", {"request": request})


@app.get("/assignments", response_class=HTMLResponse)
async def assignments_page(request: Request):
    return templates.TemplateResponse("assignments.html", {"request": request})


@app.get("/results", response_class=HTMLResponse)
async def results_page(request: Request):
    return templates.TemplateResponse("results.html", {"request": request})


@app.get("/notices", response_class=HTMLResponse)
async def notices_page(request: Request):
    return templates.TemplateResponse("notices.html", {"request": request})


@app.get("/timetable", response_class=HTMLResponse)
async def timetable_page(request: Request):
    return templates.TemplateResponse("timetable.html", {"request": request})


@app.get("/assignments", response_class=HTMLResponse)
async def assignments_page(request: Request):
    return templates.TemplateResponse("assignments.html", {"request": request})


@app.get("/assignments/{assignment_id}", response_class=HTMLResponse)
async def assignment_details_page(request: Request, assignment_id: int):
    return templates.TemplateResponse("assignment_details.html", {"request": request, "assignment_id": assignment_id})


@app.get("/submissions/{submission_id}", response_class=HTMLResponse)
async def submission_page(request: Request, submission_id: int):
    return templates.TemplateResponse("submission.html", {"request": request, "submission_id": submission_id})