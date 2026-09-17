import reflex as rx
from college_erp.services.api import api
from college_erp.state.auth_state import AuthState
from typing import List, Dict, Any, Optional
import json


class NoticesState(rx.State):
    """State management for notices."""

    notices: List[Dict[str, Any]] = []
    loading: bool = False
    error: str = ""
    show_create_form: bool = False

    # Form fields for creating notice
    title: str = ""
    content: str = ""
    target_audience: str = "all"
    department_id: Optional[int] = None
    departments: List[Dict[str, Any]] = []

    @rx.background
    async def load_notices(self):
        """Load notices from API."""
        async with self:
            self.loading = True
            self.error = ""

        try:
            response = await api.get_notices()
            async with self:
                self.loading = False
                self.notices = response if isinstance(response, list) else []

        except Exception as e:
            async with self:
                self.loading = False
                self.error = str(e)

    @rx.background
    async def load_departments(self):
        """Load departments for dropdown in create form."""
        async with self:
            self.loading = True
            self.error = ""

        try:
            response = await api.get_departments()
            async with self:
                self.loading = False
                self.departments = response if isinstance(response, list) else []

        except Exception as e:
            async with self:
                self.loading = False
                self.error = str(e)
            # Fallback departments
            async with self:
                self.departments = [
                    {"id": 1, "name": "Computer Science & Engineering", "code": "CSE"},
                    {"id": 2, "name": "Electronics & Communication", "code": "ECE"},
                    {"id": 3, "name": "Mechanical Engineering", "code": "MECH"},
                    {"id": 4, "name": "Business Administration", "code": "MBA"},
                ]

    def toggle_create_form(self):
        """Toggle the create notice form."""
        self.show_create_form = not self.show_create_form
        if self.show_create_form:
            self.load_departments()
        # Reset form when closing
        if not self.show_create_form:
            self.title = ""
            self.content = ""
            self.target_audience = "all"
            self.department_id = None

    @rx.background
    async def create_notice(self):
        """Create a new notice."""
        async with self:
            self.loading = True
            self.error = ""

        try:
            # Validate form
            if not self.title.strip():
                raise ValueError("Title is required")
            if not self.content.strip():
                raise ValueError("Content is required")

            # Get current user ID
            user_data = await api.get_me()
            user_id = user_data["user_id"]

            # Create notice
            response = await api.create_notice(
                title=self.title.strip(),
                content=self.content.strip(),
                target_audience=self.target_audience,
                department_id=self.department_id
            )

            async with self:
                self.loading = False
                # Reset form
                self.title = ""
                self.content = ""
                self.target_audience = "all"
                self.department_id = None
                self.show_create_form = False

                # Refresh notices list
                await self.load_notices()

                # Show success
                rx.toast.success("Notice created successfully!")

        except Exception as e:
            async with self:
                self.loading = False
                self.error = str(e)
                rx.toast.error(f"Failed to create notice: {str(e)}")

    @rx.background
    async def update_notice(self, notice_id: int):
        """Update an existing notice."""
        async with self:
            self.loading = True
            self.error = ""

        try:
            # Validate form
            if not self.title.strip():
                raise ValueError("Title is required")
            if not self.content.strip():
                raise ValueError("Content is required")

            # Update notice
            response = await api.update_notice(
                notice_id=notice_id,
                title=self.title.strip(),
                content=self.content.strip(),
                target_audience=self.target_audience,
                department_id=self.department_id
            )

            async with self:
                self.loading = False
                # Reset form
                self.title = ""
                self.content = ""
                self.target_audience = "all"
                self.department_id = None
                self.show_create_form = False

                # Refresh notices list
                await self.load_notices()

                # Show success
                rx.toast.success("Notice updated successfully!")

        except Exception as e:
            async with self:
                self.loading = False
                self.error = str(e)
                rx.toast.error(f"Failed to update notice: {str(e)}")

    @rx.background
    async def delete_notice(self, notice_id: int):
        """Delete a notice."""
        async with self:
            self.loading = True
            self.error = ""

        try:
            # Delete notice
            await api.delete_notice(notice_id)

            async with self:
                self.loading = False

                # Refresh notices list
                await self.load_notices()

                # Show success
                rx.toast.success("Notice deleted successfully!")

        except Exception as e:
            async with self:
                self.loading = False
                self.error = str(e)
                rx.toast.error(f"Failed to delete notice: {str(e)}")

    @rx.event
    async def refresh_notices(self):
        """Refresh the notices list."""
        await self.load_notices()