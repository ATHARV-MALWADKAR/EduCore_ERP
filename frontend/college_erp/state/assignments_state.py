import reflex as rx
from college_erp.services.api import api
from college_erp.state.auth_state import AuthState
from typing import List, Dict, Any, Optional
import json


class AssignmentsState(rx.State):
    """State management for assignments."""

    assignments: List[Dict[str, Any]] = []
    loading: bool = False
    error: str = ""
    show_create_form: bool = False

    # Form fields for creating assignment
    title: str = ""
    description: str = ""
    due_at: str = ""
    subject_id: Optional[int] = None
    status: str = "published"
    subjects: List[Dict[str, Any]] = []

    @rx.background
    async def load_assignments(self):
        """Load assignments from API."""
        async with self:
            self.loading = True
            self.error = ""

        try:
            # Get user info to determine what assignments to show
            user_data = await api.get_me()
            async with self:
                self.loading = False

            if user_data.get("role") == "faculty":
                # Faculty sees their own assignments
                # Need to get faculty profile first to get subjects they teach
                # For now, get all assignments and filter later or use endpoint
                response = await api.get_assignments()
                async with self:
                    self.assignments = response if isinstance(response, list) else []
            else:
                # Student sees assignments for their enrolled subjects
                # Get student profile first
                student_data = await api.get_student_profile(user_data["user_id"])
                # For simplicity, get all assignments (would filter by subjects in real implementation)
                response = await api.get_assignments()
                async with self:
                    self.assignments = response if isinstance(response, list) else []

        except Exception as e:
            async with self:
                self.loading = False
                self.error = str(e)

    @rx.background
    async def load_subjects(self):
        """Load subjects for dropdown in create form."""
        async with self:
            self.loading = True
            self.error = ""

        try:
            response = await api.get_courses()  # Actually need subjects endpoint
            # For now, we'll simulate subjects or get from a different endpoint
            # This would be improved with a proper subjects endpoint
            async with self:
                self.loading = False
                self.subjects = [
                    {"id": 1, "name": "Data Structures & Algorithms", "code": "CS201"},
                    {"id": 2, "name": "Database Management Systems", "code": "CS301"},
                    {"id": 3, "name": "Operating Systems", "code": "CS302"},
                    {"id": 4, "name": "Software Engineering & ERP", "code": "CS401"},
                ]
        except Exception as e:
            async with self:
                self.loading = False
                self.error = str(e)
            # Fallback subjects
            async with self:
                self.subjects = [
                    {"id": 1, "name": "Data Structures & Algorithms", "code": "CS201"},
                    {"id": 2, "name": "Database Management Systems", "code": "CS301"},
                    {"id": 3, "name": "Operating Systems", "code": "CS302"},
                    {"id": 4, "name": "Software Engineering & ERP", "code": "CS401"},
                ]

    def toggle_create_form(self):
        """Toggle the create assignment form."""
        self.show_create_form = not self.show_create_form
        if self.show_create_form:
            self.load_subjects()
        # Reset form when closing
        if not self.show_create_form:
            self.title = ""
            self.description = ""
            self.due_at = ""
            self.subject_id = None
            self.status = "published"

    @rx.background
    async def create_assignment(self):
        """Create a new assignment."""
        async with self:
            self.loading = True
            self.error = ""

        try:
            # Validate form
            if not self.title.strip():
                raise ValueError("Title is required")
            if not self.description.strip():
                raise ValueError("Description is required")
            if not self.due_at.strip():
                raise ValueError("Due date is required")
            if self.subject_id is None:
                raise ValueError("Subject is required")

            # Get current user ID
            user_data = await api.get_me()
            user_id = user_data["user_id"]

            # Create assignment
            response = await api.create_assignment(
                subject_id=self.subject_id,
                title=self.title.strip(),
                description=self.description.strip(),
                due_at=self.due_at.strip(),
                status=self.status
            )

            async with self:
                self.loading = False
                # Reset form
                self.title = ""
                self.description = ""
                self.due_at = ""
                self.subject_id = None
                self.status = "published"
                self.show_create_form = False

                # Refresh assignments list
                await self.load_assignments()

                # Show success (in a real app, we'd use toast notifications)
                rx.toast.success("Assignment created successfully!")

        except Exception as e:
            async with self:
                self.loading = False
                self.error = str(e)
                rx.toast.error(f"Failed to create assignment: {str(e)}")

    @rx.event
    async def refresh_assignments(self):
        """Refresh the assignments list."""
        await self.load_assignments()