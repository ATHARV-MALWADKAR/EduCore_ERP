import reflex as rx
from college_erp.services.api import api
from college_erp.state.auth_state import AuthState
from typing import List, Dict, Any, Optional
import json
from datetime import date, datetime


class FacultyDashboardState(rx.State):
    """State management for faculty dashboard."""

    # Today's classes data
    todays_classes: List[Dict[str, Any]] = []
    classes_loading: bool = False
    classes_error: str = ""

    # Assignments to review
    pending_submissions: int = 0
    graded_today: int = 0
    assignments_loading: bool = False
    assignments_error: str = ""

    # Attendance management
    attendance_loading: bool = False
    attendance_error: str = ""
    today_attendance_marked: bool = False

    # Notices
    recent_notices: List[Dict[str, Any]] = []
    notices_loading: bool = False
    notices_error: str = ""

    @rx.background
    async def load_todays_classes(self):
        """Load today's classes for faculty dashboard."""
        async with self:
            self.classes_loading = True
            self.classes_error = ""

        try:
            # Get faculty profile first
            user_data = await api.get_me()
            faculty_data = await api.get_faculty_profile(user_data["user_id"])
            faculty_id = faculty_data["id"]

            # Get today's timetable
            today_weekday = date.today().isoweekday()  # Monday=1, Sunday=7
            timetable_data = await api.get_timetable()  # Would filter by faculty and date in real implementation

            async with self:
                self.classes_loading = False
                # Placeholder data for today's classes
                self.todays_classes = [
                    {
                        "subject": "Data Structures & Algorithms",
                        "time": "9:00 AM - 10:00 AM",
                        "room": "Lab-301",
                        "type": "Lecture"
                    },
                    {
                        "subject": "Database Management Systems",
                        "time": "11:00 AM - 12:00 PM",
                        "room": "Room-102",
                        "type": "Lecture"
                    }
                ]

        except Exception as e:
            async with self:
                self.classes_loading = False
                self.classes_error = str(e)

    @rx.background
    async def load_assignments_data(self):
        """Load assignments data for faculty dashboard."""
        async with self:
            self.assignments_loading = True
            self.assignments_error = ""

        try:
            # Get faculty profile first
            user_data = await api.get_me()
            faculty_data = await api.get_faculty_profile(user_data["user_id"])
            faculty_id = faculty_data["id"]

            # Get assignments by faculty
            assignments_data = await api.get_assignments_by_faculty(faculty_id)

            async with self:
                self.assignments_loading = False
                # Placeholder data
                self.pending_submissions = 5
                self.graded_today = 3

        except Exception as e:
            async with self:
                self.assignments_loading = False
                self.assignments_error = str(e)

    @rx.background
    async def load_attendance_data(self):
        """Load attendance management data."""
        async with self:
            self.attendance_loading = True
            self.attendance_error = ""

        try:
            # Get faculty profile first
            user_data = await api.get_me()
            faculty_data = await api.get_faculty_profile(user_data["user_id"])
            faculty_id = faculty_data["id"]

            # Check if attendance already marked today
            async with self:
                self.attendance_loading = False
                self.today_attendance_marked = False  # Placeholder

        except Exception as e:
            async with self:
                self.attendance_loading = False
                self.attendance_error = str(e)

    @rx.background
    async def load_notices_data(self):
        """Load notices data for faculty dashboard."""
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
    async def mark_todays_attendance(self):
        """Mark attendance for today's classes."""
        # This would open a modal or form to mark attendance
        async with self:
            self.today_attendance_marked = True
        rx.toast.success("Attendance marked for today's classes!")

    @rx.event
    async def load_all_data(self):
        """Load all dashboard data."""
        await self.load_todays_classes()
        await self.load_assignments_data()
        await self.load_attendance_data()
        await self.load_notices_data()