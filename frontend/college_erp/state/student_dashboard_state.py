import reflex as rx
from college_erp.services.api import api
from college_erp.state.auth_state import AuthState
from typing import List, Dict, Any, Optional
import json


class StudentDashboardState(rx.State):
    """State management for student dashboard."""

    # Attendance data
    attendance_percentage: float = 0.0
    total_classes: int = 0
    attended_classes: int = 0
    attendance_loading: bool = False
    attendance_error: str = ""

    # Assignments data
    pending_assignments: int = 0
    submitted_assignments: int = 0
    graded_assignments: int = 0
    assignments_loading: bool = False
    assignments_error: str = ""

    # Results data
    recent_results: List[Dict[str, Any]] = []
    results_loading: bool = False
    results_error: str = ""

    # Notices data
    recent_notices: List[Dict[str, Any]] = []
    notices_loading: bool = False
    notices_error: str = ""

    @rx.background
    async def load_attendance_data(self):
        """Load attendance data for student dashboard."""
        async with self:
            self.attendance_loading = True
            self.attendance_error = ""

        try:
            # Get student profile first
            user_data = await api.get_me()
            student_data = await api.get_student_profile(user_data["user_id"])
            student_id = student_data["id"]

            # Get attendance summary
            attendance_data = await api.get_student_attendance(student_id)

            async with self:
                self.attendance_loading = False
                if attendance_data:
                    self.attendance_percentage = attendance_data.get("percentage", 0.0)
                    self.total_classes = attendance_data.get("total_classes", 0)
                    self.attended_classes = attendance_data.get("attended_classes", 0)

        except Exception as e:
            async with self:
                self.attendance_loading = False
                self.attendance_error = str(e)

    @rx.background
    async def load_assignments_data(self):
        """Load assignments data for student dashboard."""
        async with self:
            self.assignments_loading = True
            self.assignments_error = ""

        try:
            # Get student profile first
            user_data = await api.get_me()
            student_data = await api.get_student_profile(user_data["user_id"])
            student_id = student_data["id"]

            # Get assignments (would need endpoint for student assignments)
            # For now, we'll simulate or use a placeholder
            async with self:
                self.assignments_loading = False
                # Placeholder data - would come from actual API calls
                self.pending_assignments = 3
                self.submitted_assignments = 2
                self.graded_assignments = 1

        except Exception as e:
            async with self:
                self.assignments_loading = False
                self.assignments_error = str(e)

    @rx.background
    async def load_results_data(self):
        """Load results data for student dashboard."""
        async with self:
            self.results_loading = True
            self.results_error = ""

        try:
            # Get student profile first
            user_data = await api.get_me()
            student_data = await api.get_student_profile(user_data["user_id"])
            student_id = student_data["id"]

            # Get results
            results_data = await api.get_results(student_id)

            async with self:
                self.results_loading = False
                self.recent_results = results_data if isinstance(results_data, list) else []

        except Exception as e:
            async with self:
                self.results_loading = False
                self.results_error = str(e)

    @rx.background
    async def load_notices_data(self):
        """Load notices data for student dashboard."""
        async with self:
            self.notices_loading = True
            self.notices_error = ""

        try:
            # Get recent notices
            notices_data = await api.get_notices(limit=5)

            async with self:
                self.notices_loading = False
                self.recent_notices = notices_data if isinstance(notices_data, list) else []

        except Exception as e:
            async with self:
                self.notices_loading = False
                self.notices_error = str(e)

    @rx.event
    async def load_all_data(self):
        """Load all dashboard data."""
        await self.load_attendance_data()
        await self.load_assignments_data()
        await self.load_results_data()
        await self.load_notices_data()