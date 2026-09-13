from fastapi import APIRouter
from app.api.v1.routes_auth import router as auth_router
from app.api.v1.routes_students import router as students_router
from app.api.v1.routes_faculty import router as faculty_router
from app.api.v1.routes_admin import router as admin_router
from app.api.v1.routes_attendance import router as attendance_router
# from app.api.v1.routes_assignments import router as assignments_router
# from app.api.v1.routes_results import router as results_router
# from app.api.v1.routes_notices import router as notices_router
# from app.api.v1.routes_timetable import router as timetable_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
router.include_router(admin_router, prefix="/admin", tags=["Administration"])
router.include_router(students_router, prefix="/students", tags=["Students"])
router.include_router(faculty_router, prefix="/faculty", tags=["Faculty"])
router.include_router(attendance_router, prefix="/attendance", tags=["Attendance"])
# router.include_router(assignments_router, prefix="/assignments", tags=["Assignments"])
# router.include_router(results_router, prefix="/results", tags=["Results"])
# router.include_router(notices_router, prefix="/notices", tags=["Notices"])
# router.include_router(timetable_router, prefix="/timetable", tags=["Timetable"])
