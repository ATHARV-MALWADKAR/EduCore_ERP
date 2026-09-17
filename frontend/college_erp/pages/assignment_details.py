import reflex as rx
from college_erp.components.layouts import dashboard_layout
from college_erp.state.auth_state import AuthState
from college_erp.state.assignments_state import AssignmentsState
from college_erp.state.submission_state import SubmissionState


@rx.page(route="/assignments/[id]", title="Assignment Details")
def assignment_details() -> rx.Component:
    return dashboard_layout(
        rx.vstack(
            rx.heading("Assignment Details", size="lg"),
            rx.cond(
                SubmissionState.loading,
                rx.center(rx.spinner(size="3"), height="200px"),
                rx.cond(
                    SubmissionState.error != "",
                    rx.alert(
                        rx.alert_icon(),
                        rx.alert_title("Error"),
                        rx.alert_description(SubmissionState.error),
                        status="error",
                    ),
                    rx.vstack(
                        # Assignment Info Section
                        rx.box(
                            rx.vstack(
                                rx.heading("Assignment Information", size="md"),
                                rx.grid(
                                    rx.vstack(
                                        rx.text("Title:", font_weight="medium"),
                                                        rx.text(AssignmentsState.assignments[0].get("title", "Loading...") if AssignmentsState.assignments else "Loading..."),
                                    ),
                                    rx.vstack(
                                        rx.text("Subject:", font_weight="medium"),
                                                        rx.text(AssignmentsState.assignments[0].get("subject_name", "Loading...") if AssignmentsState.assignments else "Loading..."),
                                    ),
                                    rx.vstack(
                                        rx.text("Due Date:", font_weight="medium"),
                                                        rx.text(
                                            AssignmentsState.assignments[0].get("due_at", "TBD")[:10]
                                            if AssignmentsState.assignments and AssignmentsState.assignments[0].get("due_at")
                                            else "TBD"
                                        ),
                                    ),
                                    rx.vstack(
                                        rx.text("Status:", font_weight="medium"),
                                                        rx.badge(
                                            AssignmentsState.assignments[0].get("status", "unknown").title()
                                            if AssignmentsState.assignments else "Loading...",
                                            color_scheme=(
                                                "green" if AssignmentsState.assignments and AssignmentsState.assignments[0].get("status") == "published"
                                                else "orange" if AssignmentsState.assignments and AssignmentsState.assignments[0].get("status") == "draft"
                                                else "red" if AssignmentsState.assignments and AssignmentsState.assignments[0].get("status") == "closed"
                                                else "gray"
                                            ),
                                            variant="soft"
                                        ),
                                    ),
                                    template_columns="repeat(2, 1fr)",
                                    gap="4",
                                    width="100%",
                                ),
                                rx.cond(
                                    AssignmentsState.assignments and AssignmentsState.assignments[0].get("description"),
                                    rx.vstack(
                                        rx.text("Description:", font_weight="medium", class_name="mb-2"),
                                                        rx.text(AssignmentsState.assignments[0].get("description", ""), white_space="pre-line"),
                                                    ),
                                ),
                                spacing="4",
                                width="100%",
                            ),
                            background_color="white",
                            padding="4",
                            border_radius="lg",
                            box_shadow="sm",
                            width="100%",
                        ),

                        # Submission Section
                        rx.cond(
                            AuthState.role == "student",
                            rx.vstack(
                                rx.heading("Your Submission", size="md"),
                                rx.cond(
                                    SubmissionState.submissions.length() > 0,
                                    rx.vstack(
                                        rx.foreach(
                                            SubmissionState.submissions,
                                            lambda submission: student_submission_view(submission)
                                        ),
                                        spacing="4",
                                    ),
                                    rx.vstack(
                                        rx.icon("file-text", size=48, color="gray.400"),
                                                        rx.text("You haven't submitted this assignment yet", color="gray.500"),
                                                        rx.button(
                                            "Submit Assignment",
                                            on_click=lambda: rx.redirect(
                                                f"/assignments/{rx.State.router.page.params.get('id', '')}/submit"
                                            ),
                                            background_color="#2563eb",
                                            color="white",
                                            _hover={"background_color": "#1d4ed8"},
                                        ),
                                        spacing="4",
                                        align_items="center",
                                    ),
                                ),
                                spacing="4",
                                width="100%",
                            ),
                            rx.cond(
                                AuthState.role == "faculty",
                                rx.vstack(
                                    rx.heading("Student Submissions", size="md"),
                                    rx.cond(
                                        SubmissionState.submissions.length() > 0,
                                        rx.vstack(
                                            rx.foreach(
                                                SubmissionState.submissions,
                                                lambda submission: faculty_submission_view(submission)
                                            ),
                                            spacing="4",
                                        ),
                                        rx.vstack(
                                            rx.icon("inbox", size=48, color="gray.400"),
                                                        rx.text("No submissions yet", color="gray.500"),
                                            spacing="4",
                                            align_items="center",
                                        ),
                                    ),
                                    spacing="4",
                                    width="100%",
                                ),
                            ),
                        ),
                        spacing="6",
                        width="100%",
                    ),
                ),
            ),
            spacing="4",
            width="100%",
        )
    )


def student_submission_view(submission: dict) -> rx.Component:
    """View for student's own submission"""
    # Format dates
    submitted_at = "Unknown"
    if submission.get("submitted_at"):
        try:
            submitted_at = rx.utils.format_date(submission["submitted_at"], "MMM d, yyyy h:mm a")
        except:
            submitted_at = submission["submitted_at"][:16] if len(submission["submitted_at"]) >= 16 else submission["submitted_at"]

    updated_at = "Unknown"
    if submission.get("updated_at"):
        try:
            updated_at = rx.utils.format_date(submission["updated_at"], "MMM d, yyyy h:mm a")
        except:
            updated_at = submission["updated_at"][:16] if len(submission["updated_at"]) >= 16 else submission["updated_at"]

    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.heading("Your Submission", size="md"),
                    rx.hstack(
                        rx.badge(
                            f"Submitted: {submitted_at}",
                            color_scheme="blue",
                            variant="soft",
                            font_size="0.75rem",
                        ),
                        rx.badge(
                            f"Updated: {updated_at}",
                            color_scheme="gray",
                            variant="soft",
                            font_size="0.75rem",
                        ),
                        spacing="2",
                    ),
                    width="100%",
                ),
                rx.spacer(),
                rx.cond(
                    submission.get("marks_given") is not None,
                    rx.vstack(
                        rx.badge(
                            f"Score: {submission['marks_given']}",
                            color_scheme="green",
                            variant="solid",
                            font_size="0.875rem",
                        ),
                        rx.cond(
                            submission.get("feedback"),
                            rx.text(
                                submission["feedback"],
                                font_size="0.875rem",
                                color="gray.600",
                                margin_top="0.5rem",
                            ),
                        ),
                        align_items="end",
                    ),
                ),
                width="100%",
                align_items="start",
            ),
            rx.cond(
                submission.get("content"),
                rx.vstack(
                    rx.text("Submission Content:", font_weight="medium"),
                    rx.text(
                        submission["content"],
                        background_color="gray.50",
                        padding="1rem",
                        border_radius="md",
                        font_family="monospace",
                        font_size="0.875rem",
                        white_space="pre-wrap",
                        max_height="200px",
                        overflow_y="auto",
                    ),
                ),
            ),
            rx.cond(
                submission.get("file_path"),
                rx.vstack(
                    rx.text("Attached File:", font_weight="medium"),
                    rx.link(
                        submission["file_path"].split("/")[-1],  # Show just filename
                        href=submission["file_path"],
                        color="#2563eb",
                        text_decoration="underline",
                    ),
                ),
            ),
            width="100%",
            spacing="4",
        ),
        width="100%",
        box_shadow="sm",
    )


def faculty_submission_view(submission: dict) -> rx.Component:
    """View for faculty to see and grade submissions"""
    # Get student info
    student_name = submission.get("student_name", "Unknown Student")
    roll_number = submission.get("roll_number", "N/A")

    # Format dates
    submitted_at = "Unknown"
    if submission.get("submitted_at"):
        try:
            submitted_at = rx.utils.format_date(submission["submitted_at"], "MMM d, yyyy h:mm a")
        except:
            submitted_at = submission["submitted_at"][:16] if len(submission["submitted_at"]) >= 16 else submission["submitted_at"]

    updated_at = "Unknown"
    if submission.get("updated_at"):
        try:
            updated_at = rx.utils.format_date(submission["updated_at"], "MMM d, yyyy h:mm a")
        except:
            updated_at = submission["updated_at"][:16] if len(submission["updated_at"]) >= 16 else submission["updated_at"]

    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.heading(f"Submission by {student_name}", size="md"),
                    rx.hstack(
                        rx.badge(
                            f"Roll: {roll_number}",
                            color_scheme="blue",
                            variant="soft",
                            font_size="0.75rem",
                        ),
                        rx.badge(
                            f"Submitted: {submitted_at}",
                            color_scheme="blue",
                            variant="soft",
                            font_size="0.75rem",
                        ),
                        rx.badge(
                            f"Updated: {updated_at}",
                            color_scheme="gray",
                            variant="soft",
                            font_size="0.75rem",
                        ),
                        spacing="2",
                    ),
                    width="100%",
                ),
                rx.spacer(),
                rx.cond(
                    submission.get("marks_given") is not None,
                    rx.vstack(
                        rx.badge(
                            f"Score: {submission['marks_given']}",
                            color_scheme="green",
                            variant="solid",
                            font_size="0.875rem",
                        ),
                    ),
                    rx.cond(
                        submission.get("marks_given") is None,
                        rx.button(
                            "Grade Submission",
                            on_click=lambda: SubmissionState.set_grading_submission(submission["id"]),
                            background_color="#10b981",
                            color="white",
                            _hover={"background_color": "#059669"},
                        ),
                    ),
                    align_items="end",
                ),
                width="100%",
                align_items="start",
            ),
            rx.cond(
                submission.get("content"),
                rx.vstack(
                    rx.text("Submission Content:", font_weight="medium"),
                    rx.text(
                        submission["content"],
                        background_color="gray.50",
                        padding="1rem",
                        border_radius="md",
                        font_family="monospace",
                        font_size="0.875rem",
                        white_space="pre-wrap",
                        max_height="150px",
                        overflow_y="auto",
                    ),
                ),
            ),
            rx.cond(
                submission.get("file_path"),
                rx.vstack(
                    rx.text("Attached File:", font_weight="medium"),
                    rx.link(
                        submission["file_path"].split("/")[-1],  # Show just filename
                        href=submission["file_path"],
                        color="#2563eb",
                        text_decoration="underline",
                    ),
                ),
            ),
            width="100%",
            spacing="4",
        ),
        width="100%",
        box_shadow="sm",
    )