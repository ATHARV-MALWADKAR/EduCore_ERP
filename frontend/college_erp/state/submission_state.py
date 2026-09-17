import reflex as rx
from college_erp.services.api import api
from college_erp.state.auth_state import AuthState
from typing import List, Dict, Any, Optional
import json


class SubmissionState(rx.State):
    """State management for submissions."""

    submissions: List[Dict[str, Any]] = []
    loading: bool = False
    error: str = ""
    assignment_id: Optional[int] = None
    grading_submission_id: Optional[int] = None

    # Grading form fields
    marks_given: Optional[float] = None
    feedback: str = ""

    @rx.background
    async def load_submissions(self, assignment_id: int):
        """Load submissions for an assignment."""
        async with self:
            self.loading = True
            self.error = ""
            self.assignment_id = assignment_id
            self.grading_submission_id = None  # Reset grading selection
            self.clear_grading_form()

        try:
            response = await api.get_submissions(assignment_id)
            async with self:
                self.loading = False
                self.submissions = response if isinstance(response, list) else []

        except Exception as e:
            async with self:
                self.loading = False
                self.error = str(e)

    def set_grading_submission(self, submission_id: int):
        """Set which submission to grade."""
        self.grading_submission_id = submission_id
        # Clear form when selecting new submission
        self.clear_grading_form()

    def clear_grading_form(self):
        """Clear the grading form."""
        self.marks_given = None
        self.feedback = ""

    @rx.background
    async def grade_submission(self, submission_id: int):
        """Grade a submission."""
        async with self:
            self.loading = True
            self.error = ""

        try:
            # Validate form
            if self.marks_given is None:
                raise ValueError("Marks are required")
            if self.marks_given < 0:
                raise ValueError("Marks cannot be negative")

            # Grade the submission
            response = await api.grade_submission(
                submission_id=submission_id,
                marks_given=self.marks_given,
                feedback=self.feedback.strip() if self.feedback.strip() else None
            )

            async with self:
                self.loading = False
                # Clear form and selection
                self.clear_grading_form()
                self.grading_submission_id = None

                # Refresh submissions list
                if self.assignment_id:
                    await self.load_submissions(self.assignment_id)

                # Show success
                rx.toast.success("Submission graded successfully!")

        except Exception as e:
            async with self:
                self.loading = False
                self.error = str(e)
                rx.toast.error(f"Failed to grade submission: {str(e)}")

    @rx.event
    async def refresh_submissions(self):
        """Refresh the submissions list."""
        if self.assignment_id:
            await self.load_submissions(self.assignment_id)