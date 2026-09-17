import reflex as rx
from college_erp.state.auth_state import AuthState
from college_erp.state.submission_state import SubmissionState
from college_erp.state.assignments_state import AssignmentsState


def submission_details(assignment_id: int) -> rx.Component:
    return rx.cond(
        SubmissionState.loading,
        rx.center(rx.spinner(size="3"), height="200px"),
        rx.cond(
            SubmissionState.error != "",
            rx.alert(
                rx.alert_icon(),
                rx.alert_title("Error"),
                rx.alert_description(SubmissionState.error),
                status="error",
                margin_bottom="1rem",
            ),
            rx.vstack(
                rx.hstack(
                    rx.heading("Assignment Details", size="md"),
                    rx.spacer(),
                    rx.button(
                        "Back to Assignments",
                        on_click=rx.redirect("/assignments"),
                        variant="outline",
                        size="2",
                    ),
                    width="100%",
                    align_items="center",
                ),
                rx.box(
                    rx.vstack(
                        rx.heading("Assignment Information", size="lg"),
                        rx.grid(
                            rx.vstack(
                                rx.text("Title:", font_weight="medium"),
                                rx.text(AssignmentsState.assignments[0].get("title", "Loading...") if AssignmentsState.assignments else "Loading..."),
                            ),
                            rx.vstack(
                                rx.text("Description:", font_weight="medium"),
                                rx.text(AssignmentsState.assignments[0].get("description", "No description") if AssignmentsState.assignments else "Loading..."),
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
                            gap="2",
                            width="100%",
                        ),
                        margin_bottom="2rem",
                    ),
                    rx.cond(
                        AuthState.role == "student",
                        rx.vstack(
                            rx.heading("Your Submission", size="md"),
                            rx.cond(
                                SubmissionState.submissions.length() > 0,
                                rx.vstack(
                                    rx.foreach(
                                        SubmissionState.submissions,
                                        lambda submission: student_submission_card(submission)
                                    ),
                                    spacing="3",
                                ),
                                rx.vstack(
                                    rx.icon("file-text", size=48, color="gray.400"),
                                    rx.text("You haven't submitted this assignment yet", color="gray.500"),
                                    rx.button(
                                        "Submit Assignment",
                                        on_click=lambda: rx.redirect(
                                            f"/assignments/{assignment_id}/submit"
                                        ),
                                        background_color="#2563eb",
                                        color="white",
                                        _hover={"background_color": "#1d4ed8"},
                                    ),
                                    spacing="3",
                                    align_items="center",
                                ),
                            ),
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
                                            lambda submission: faculty_submission_card(submission)
                                        ),
                                        spacing="3",
                                    ),
                                    rx.vstack(
                                        rx.icon("inbox", size=48, color="gray.400"),
                                        rx.text("No submissions yet", color="gray.500"),
                                        spacing="3",
                                        align_items="center",
                                    ),
                                ),
                            ),
                        ),
                        width="100%",
                    ),
                    background_color="white",
                    padding="2rem",
                    border_radius="lg",
                    box_shadow="sm",
                ),
                spacing="4",
                width="100%",
            ),
        ),
    )


def student_submission_card(submission: dict) -> rx.Component:
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


def faculty_submission_card(submission: dict) -> rx.Component:
    # Get student info (would ideally come from API with joined load)
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


def submission_grading_form(assignment_id: int) -> rx.Component:
    # Get the submission to grade (would be set when clicking grade button)
    submission_id = SubmissionState.grading_submission_id if hasattr(SubmissionState, 'grading_submission_id') else None

    return rx.cond(
        submission_id is not None,
        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.heading("Grade Submission", size="lg"),
                    rx.spacer(),
                    rx.button(
                        rx.icon("x", size=20),
                        on_click=SubmissionState.clear_grading_form,
                        color_scheme="red",
                        variant="ghost",
                        size="2",
                    ),
                    width="100%",
                    align_items="center",
                ),
                rx.form(
                    rx.vstack(
                        rx.grid(
                            rx.vstack(
                                rx.label("Marks Obtained", font_weight="medium"),
                                rx.input(
                                    type="number",
                                    step="0.01",
                                    min="0",
                                    placeholder="Enter marks",
                                    value=SubmissionState.marks_given,
                                    on_change=SubmissionState.set_marks_given,
                                    required=True,
                                    width="100%",
                                ),
                            ),
                            rx.vstack(
                                rx.label("Maximum Marks", font_weight="medium"),
                                rx.input(
                                    type="number",
                                    step="0.01",
                                    min="0.01",
                                    value="100",  # This should come from assignment/quiz settings
                                    read_only=True,
                                    width="100%",
                                ),
                            ),
                            template_columns="repeat(auto-fit, minmax(250px, 1fr))",
                            gap="1.5rem",
                            width="100%",
                        ),
                        rx.vstack(
                            rx.label("Feedback (Optional)", font_weight="medium"),
                            rx.text_area(
                                placeholder="Provide feedback for the student...",
                                value=SubmissionState.feedback,
                                on_change=SubmissionState.set_feedback,
                                rows="4",
                                width="100%",
                            ),
                        ),
                        rx.divider(),
                        rx.hstack(
                            rx.button(
                                "Cancel",
                                on_click=SubmissionState.clear_grading_form,
                                variant="outline",
                                color_scheme="gray",
                            ),
                            rx.spacer(),
                            rx.button(
                                "Submit Grade",
                                type="submit",
                                background_color="#10b981",
                                color="white",
                                _hover={"background_color": "#059669"},
                                is_loading=SubmissionState.loading,
                            ),
                            width="100%",
                            align_items="center",
                        ),
                        spacing="4",
                        width="100%",
                    ),
                    on_submit=SubmissionState.grade_submission,
                    reset_on_submit=False,
                    width="100%",
                ),
                spacing="4",
                width="100%",
            ),
            width="100%",
        ),
        rx.box(),  # Empty box when no submission selected for grading
    )