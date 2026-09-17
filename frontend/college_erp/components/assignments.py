import reflex as rx
from college_erp.state.auth_state import AuthState
from college_erp.state.assignments_state import AssignmentsState
from college_erp.state.submission_state import SubmissionState


def assignment_list() -> rx.Component:
    return rx.cond(
        AssignmentsState.loading,
        rx.center(rx.spinner(size="3"), height="200px"),
        rx.cond(
            AssignmentsState.error != "",
            rx.alert(
                rx.alert_icon(),
                rx.alert_title("Error"),
                rx.alert_description(AssignmentsState.error),
                status="error",
                margin_bottom="1rem",
            ),
            rx.vstack(
                rx.cond(
                    AuthState.role == "faculty",
                    rx.hstack(
                        rx.heading("My Assignments", size="md"),
                        rx.spacer(),
                        rx.button(
                            "Refresh",
                            on_click=AssignmentsState.refresh_assignments,
                            size="2",
                            variant="outline",
                        ),
                        width="100%",
                        align_items="center",
                    ),
                    rx.heading("Available Assignments", size="md"),
                ),
                rx.cond(
                    AssignmentsState.length() > 0,
                    rx.grid(
                        rx.foreach(
                            AssignmentsState.assignments,
                            lambda assignment: assignment_card(assignment)
                        ),
                        template_columns="repeat(auto-fit, minmax(300px, 1fr))",
                        gap="1.5rem",
                        width="100%",
                    ),
                    rx.center(
                        rx.vstack(
                            rx.icon("inbox", size=48, color="gray.400"),
                            rx.text("No assignments found", color="gray.500"),
                            spacing="2",
                        ),
                        padding="3rem",
                        text_align="center",
                    ),
                ),
                spacing="4",
                width="100%",
            ),
        ),
    )


def assignment_card(assignment: dict) -> rx.Component:
    # Format due date
    due_date = "TBD"
    if assignment.get("due_at"):
        try:
            due_date = rx.utils.format_date(assignment["due_at"], "MMM d, yyyy")
        except:
            due_date = assignment["due_at"][:10] if len(assignment["due_at"]) >= 10 else assignment["due_at"]

    # Status badge color
    status_colors = {
        "draft": "orange",
        "published": "green",
        "closed": "red"
    }
    status_color = status_colors.get(assignment.get("status", "published"), "gray")

    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.heading(assignment.get("title", "Untitled Assignment"), size="md"),
                    rx.text(
                        assignment.get("description", "No description available"),
                        color="gray.600",
                        font_size="0.875rem",
                        line_height="1.5",
                    ),
                    rx.hstack(
                        rx.badge(
                            f"Due: {due_date}",
                            color_scheme="blue",
                            variant="soft",
                            font_size="0.75rem",
                        ),
                        rx.badge(
                            assignment.get("status", "published").title(),
                            color_scheme=status_color,
                            variant="soft",
                            font_size="0.75rem",
                        ),
                        rx.spacer(),
                        rx.text(
                            f"By: {assignment.get('creator_name', 'Unknown')}",
                            font_size="0.75rem",
                            color="gray.500",
                        ),
                        width="100%",
                        wrap="wrap",
                    ),
                    width="100%",
                ),
                rx.vstack(
                    rx.cond(
                        AuthState.role == "student",
                        rx.button(
                            "Submit Assignment",
                            on_click=lambda: rx.redirect(
                                f"/assignments/{assignment.get('id')}/submit"
                            ),
                            background_color="#2563eb",
                            color="white",
                            _hover={"background_color": "#1d4ed8"},
                            width="100%",
                        ),
                        rx.button(
                            "View Submissions",
                            on_click=lambda: SubmissionState.load_submissions(assignment.get("id")),
                            background_color="#10b981",
                            color="white",
                            _hover={"background_color": "#059669"},
                            width="100%",
                        ),
                        width="100%",
                    ),
                    rx.cond(
                        AuthState.role == "faculty",
                        rx.button(
                            "Edit Assignment",
                            on_click=lambda: rx.redirect(
                                f"/assignments/{assignment.get('id')}/edit"
                            ),
                            background_color="#6b7280",
                            color="white",
                            _hover={"background_color": "#4b5563"},
                            width="100%",
                        ),
                        width="100%",
                    ),
                    margin_top="1rem",
                ),
                width="100%",
                align_items="start",
            ),
            spacing="3",
            width="100%",
        ),
        width="100%",
        box_shadow="sm",
    )


def create_assignment_form() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.heading("Create New Assignment", size="lg"),
                rx.spacer(),
                rx.button(
                    rx.icon("x", size=20),
                    on_click=AssignmentsState.toggle_create_form,
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
                            rx.label("Title", font_weight="medium"),
                            rx.input(
                                placeholder="Enter assignment title",
                                value=AssignmentsState.title,
                                on_change=AssignmentsState.set_title,
                                required=True,
                                width="100%",
                            ),
                        ),
                        rx.vstack(
                            rx.label("Subject", font_weight="medium"),
                            rx.select(
                                items=[
                                    rx.option(subject["name"], value=str(subject["id"]))
                                    for subject in AssignmentsState.subjects
                                ],
                                placeholder="Select subject",
                                value=AssignmentsState.subject_id,
                                on_change=AssignmentsState.set_subject_id,
                                required=True,
                                width="100%",
                            ),
                        ),
                        template_columns="repeat(auto-fit, minmax(250px, 1fr))",
                        gap="1.5rem",
                        width="100%",
                    ),
                    rx.vstack(
                        rx.label("Description", font_weight="medium"),
                        rx.text_area(
                            placeholder="Enter detailed description",
                            value=AssignmentsState.description,
                            on_change=AssignmentsState.set_description,
                            rows="4",
                            required=True,
                            width="100%",
                        ),
                    ),
                    rx.grid(
                        rx.vstack(
                            rx.label("Due Date", font_weight="medium"),
                            rx.input(
                                type="datetime-local",
                                value=AssignmentsState.due_at,
                                on_change=AssignmentsState.set_due_at,
                                required=True,
                                width="100%",
                            ),
                        ),
                        rx.vstack(
                            rx.label("Status", font_weight="medium"),
                            rx.select(
                                items=[
                                    rx.option("Draft", value="draft"),
                                    rx.option("Published", value="published"),
                                    rx.option("Closed", value="closed"),
                                ],
                                value=AssignmentsState.status,
                                on_change=AssignmentsState.set_status,
                                required=True,
                                width="100%",
                            ),
                        ),
                        template_columns="repeat(auto-fit, minmax(250px, 1fr))",
                        gap="1.5rem",
                        width="100%",
                    ),
                    rx.divider(),
                    rx.hstack(
                        rx.button(
                            "Cancel",
                            on_click=AssignmentsState.toggle_create_form,
                            variant="outline",
                            color_scheme="gray",
                        ),
                        rx.spacer(),
                        rx.button(
                            "Create Assignment",
                            type="submit",
                            background_color="#2563eb",
                            color="white",
                            _hover={"background_color": "#1d4ed8"},
                            is_loading=AssignmentsState.loading,
                        ),
                        width="100%",
                        align_items="center",
                    ),
                    spacing="4",
                    width="100%",
                ),
                on_submit=AssignmentsState.create_assignment,
                reset_on_submit=False,
                width="100%",
            ),
            spacing="4",
            width="100%",
        ),
        width="100%",
    )