import reflex as rx
from college_erp.state.auth_state import AuthState
from college_erp.state.student_dashboard_state import StudentDashboardState


def attendance_overview() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.heading("Attendance Overview", size="md"),
                rx.spacer(),
                rx.badge(
                    f"{StudentDashboardState.attendance_percentage:.1f}%",
                    color_scheme=(
                        "green" if StudentDashboardState.attendance_percentage >= 75
                        else "yellow" if StudentDashboardState.attendance_percentage >= 60
                        else "red"
                    ),
                    variant="solid",
                    font_size="1.25rem",
                ),
                width="100%",
                align_items="center",
            ),
            rx.vstack(
                rx.text(
                    f"{StudentDashboardState.attended_classes} / {StudentDashboardState.total_classes} classes attended",
                    color="gray.600",
                    font_size="0.875rem",
                ),
                rx.progress(
                    value=StudentDashboardState.attendance_percentage,
                    width="100%",
                    height="8px",
                ),
                rx.text(
                    rx.cond(
                        StudentDashboardState.attendance_percentage >= 75,
                        "Good attendance! Keep it up.",
                        rx.cond(
                            StudentDashboardState.attendance_percentage >= 60,
                            "Satisfactory attendance. Aim for improvement.",
                            "Low attendance. Please attend more classes."
                        ),
                    ),
                    font_size="0.75rem",
                    color=(
                        "green" if StudentDashboardState.attendance_percentage >= 75
                        else "yellow" if StudentDashboardState.attendance_percentage >= 60
                        else "red"
                    ),
                    margin_top="0.5rem",
                ),
                spacing="2",
                width="100%",
            ),
            rx.button(
                "View Detailed Attendance",
                on_click=rx.redirect("/attendance"),
                variant="outline",
                size="2",
                width="100%",
            ),
            spacing="4",
            width="100%",
        ),
        width="100%",
        box_shadow="sm",
    )


def assignments_overview() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.heading("Assignments", size="md"),
                rx.spacer(),
                rx.badge(
                    f"{StudentDashboardState.pending_assignments} Pending",
                    color_scheme="blue",
                    variant="soft",
                ),
                width="100%",
                align_items="center",
            ),
            rx.grid(
                rx.vstack(
                    rx.text("Submitted", font_weight="medium"),
                    rx.text(
                        f"{StudentDashboardState.submitted_assignments}",
                        font_size="1.5rem",
                        font_weight="bold",
                        color="green",
                    ),
                ),
                rx.vstack(
                    rx.text("Graded", font_weight="medium"),
                    rx.text(
                        f"{StudentDashboardState.graded_assignments}",
                        font_size="1.5rem",
                        font_weight="bold",
                        color="blue",
                    ),
                ),
                rx.vstack(
                    rx.text("Pending", font_weight="medium"),
                    rx.text(
                        f"{StudentDashboardState.pending_assignments}",
                        font_size="1.5rem",
                        font_weight="bold",
                        color="orange",
                    ),
                ),
                template_columns="repeat(3, 1fr)",
                gap="1",
                width="100%",
                margin_top="1rem",
            ),
            rx.button(
                "View All Assignments",
                on_click=rx.redirect("/assignments"),
                variant="outline",
                size="2",
                width="100%",
            ),
            spacing="4",
            width="100%",
        ),
        width="100%",
        box_shadow="sm",
    )


def results_overview() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.heading("Recent Results", size="md"),
                rx.spacer(),
                rx.button(
                    "View All",
                    on_click=rx.redirect("/results"),
                    variant="outline",
                    size="2",
                ),
                width="100%",
                align_items="center",
            ),
    rx.cond(
        StudentDashboardState.results_loading,
        rx.center(rx.spinner(size="3"), height="100px"),
        rx.cond(
            StudentDashboardState.results_error != "",
            rx.alert(
                rx.alert_icon(),
                rx.alert_title("Error"),
                rx.alert_description(StudentDashboardState.results_error),
                status="error",
            ),
            rx.cond(
                StudentDashboardState.recent_results.length() > 0,
                rx.vstack(
                    rx.foreach(
                        StudentDashboardState.recent_results,
                        lambda result: result_item(result)
                    ),
                    spacing="3",
                ),
                rx.vstack(
                    rx.icon("bar-chart-4", size=48, color="gray.400"),
                    rx.text("No results available yet", color="gray.500"),
                    spacing="3",
                    align_items="center",
                ),
            ),
        ),
    ),
            spacing="4",
            width="100%",
        ),
        width="100%",
        box_shadow="sm",
    )


def notices_overview() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.heading("Recent Notices", size="md"),
                rx.spacer(),
                rx.button(
                    "View All",
                    on_click=rx.redirect("/notices"),
                    variant="outline",
                    size="2",
                ),
                width="100%",
                align_items="center",
            ),
    rx.cond(
        StudentDashboardState.notices_loading,
        rx.center(rx.spinner(size="3"), height="100px"),
        rx.cond(
            StudentDashboardState.notices_error != "",
            rx.alert(
                rx.alert_icon(),
                rx.alert_title("Error"),
                rx.alert_description(StudentDashboardState.notices_error),
                status="error",
            ),
            rx.cond(
                StudentDashboardState.recent_notices.length() > 0,
                rx.vstack(
                    rx.foreach(
                        StudentDashboardState.recent_notices,
                        lambda notice: notice_item(notice)
                    ),
                    spacing="3",
                ),
                rx.vstack(
                    rx.icon("bell", size=48, color="gray.400"),
                    rx.text("No recent notices", color="gray.500"),
                    spacing="3",
                    align_items="center",
                ),
            ),
        ),
    ),
            spacing="4",
            width="100%",
        ),
        width="100%",
        box_shadow="sm",
    )


def result_item(result: dict) -> rx.Component:
    # Format date
    created_at = "Unknown"
    if result.get("created_at"):
        try:
            created_at = rx.utils.format_date(result["created_at"], "MMM d, yyyy")
        except:
            created_at = result["created_at"][:10] if len(result["created_at"]) >= 10 else result["created_at"]

    # Grade color
    grade_colors = {
        "A": "green",
        "B": "blue",
        "C": "yellow",
        "D": "orange",
        "F": "red",
    }
    grade_color = grade_colors.get(result.get("grade", ""), "gray")

    return rx.box(
        rx.hstack(
            rx.vstack(
                rx.text(result.get("subject_name", "Unknown Subject"), font_weight="medium"),
                rx.text(f"Exam: {result.get('exam_type', 'Unknown').title()}", font_size="0.75rem", color="gray.500"),
                spacing="1",
            ),
            rx.spacer(),
            rx.vstack(
                rx.text(
                    f"{result.get('marks_obtained', 0)} / {result.get('max_marks', 100)}",
                    font_size="1.25rem",
                    font_weight="bold",
                ),
                rx.badge(
                    result.get("grade", "N/A"),
                    color_scheme=grade_color,
                    variant="soft",
                ),
                spacing="1",
                align_items="end",
            ),
            width="100%",
            align_items="start",
        ),
        rx.text(
            f"Date: {created_at}",
            font_size="0.75rem",
            color="gray.400",
        ),
        spacing="3",
        width="100%",
        padding="1rem",
        background_color="gray.50",
        border_radius="md",
    )


def notice_item(notice: dict) -> rx.Component:
    # Format date
    created_at = "Unknown"
    if notice.get("created_at"):
        try:
            created_at = rx.utils.format_date(notice["created_at"], "MMM d, yyyy h:mm a")
        except:
            created_at = notice["created_at"][:16] if len(notice["created_at"]) >= 16 else notice["created_at"]

    # Target audience badge
    audience_colors = {
        "all": "blue",
        "students": "green",
        "faculty": "purple"
    }
    audience_color = audience_colors.get(notice.get("target_audience", "all"), "gray")

    return rx.box(
        rx.hstack(
            rx.vstack(
                rx.text(notice.get("title", "Untitled Notice"), font_weight="medium"),
                rx.hstack(
                    rx.badge(
                        notice.get("target_audience", "all").title(),
                        color_scheme=audience_color,
                        variant="soft",
                        font_size="0.75rem",
                    ),
                    rx.spacer(),
                    rx.text(
                        f"Posted: {created_at}",
                        font_size="0.75rem",
                        color="gray.500",
                    ),
                    width="100%",
                    wrap="wrap",
                ),
                spacing="2",
                width="100%",
            ),
            rx.spacer(),
            rx.button(
                "View",
                on_click=lambda: rx.redirect(f"/notices/{notice.get('id')}"),
                variant="outline",
                size="2",
            ),
            width="100%",
            align_items="start",
        ),
        rx.text(
            notice.get("content", "No content available")[:100] + ("..." if len(notice.get("content", "")) > 100 else ""),
            color="gray.600",
            font_size="0.875rem",
            line_height="1.4",
            max_lines="2",
        ),
        spacing="3",
        width="100%",
        padding="1rem",
        background_color="gray.50",
        border_radius="md",
    )