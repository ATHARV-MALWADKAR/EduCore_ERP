import reflex as rx
from college_erp.state.auth_state import AuthState
from college_erp.state.faculty_dashboard_state import FacultyDashboardState


def todays_classes() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.heading("Today's Classes", size="md"),
                rx.spacer(),
                rx.button(
                    "Mark Attendance",
                    on_click=FacultyDashboardState.mark_todays_attendance,
                    background_color="#10b981",
                    color="white",
                    _hover={"background_color": "#059669"},
                    size="2",
                ),
                width="100%",
                align_items="center",
            ),
            rx.cond(
                FacultyDashboardState.classes_loading,
                rx.center(rx.spinner(size="3"), height="100px"),
                rx.cond(
                    FacultyDashboardState.classes_error != "",
                    rx.alert(
                        rx.alert_icon(),
                        rx.alert_title("Error"),
                        rx.alert_description(FacultyDashboardState.classes_error),
                        status="error",
                    ),
                    rx.cond(
                        FacultyDashboardState.todays_classes.length() > 0,
                        rx.vstack(
                            rx.foreach(
                                FacultyDashboardState.todays_classes,
                                lambda class_info: class_item(class_info)
                            ),
                            spacing="3",
                        ),
                        rx.vstack(
                            rx.icon("calendar", size=48, color="gray.400"),
                            rx.text("No classes scheduled for today", color="gray.500"),
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


def assignments_to_review() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.heading("Assignments to Review", size="md"),
                rx.spacer(),
                rx.button(
                    "View All",
                    on_click=rx.redirect("/assignments"),
                    variant="outline",
                    size="2",
                ),
                width="100%",
                align_items="center",
            ),
            rx.grid(
                rx.vstack(
                    rx.text("Pending Submissions", font_weight="medium"),
                    rx.text(
                        f"{FacultyDashboardState.pending_submissions}",
                        font_size="1.5rem",
                        font_weight="bold",
                        color="orange",
                    ),
                ),
                rx.vstack(
                    rx.text("Graded Today", font_weight="medium"),
                    rx.text(
                        f"{FacultyDashboardState.graded_today}",
                        font_size="1.5rem",
                        font_weight="bold",
                        color="green",
                    ),
                ),
                template_columns="repeat(2, 1fr)",
                gap="1",
                width="100%",
                margin_top="1rem",
            ),
            rx.button(
                "Manage Assignments",
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


def attendance_management() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.heading("Attendance Management", size="md"),
                rx.spacer(),
                rx.button(
                    "View Reports",
                    on_click=rx.redirect("/attendance"),
                    variant="outline",
                    size="2",
                ),
                width="100%",
                align_items="center",
            ),
            rx.cond(
                FacultyDashboardState.attendance_loading,
                rx.center(rx.spinner(size="3"), height="100px"),
                rx.cond(
                    FacultyDashboardState.attendance_error != "",
                    rx.alert(
                        rx.alert_icon(),
                        rx.alert_title("Error"),
                        rx.alert_description(FacultyDashboardState.attendance_error),
                        status="error",
                    ),
                    rx.vstack(
                        rx.text(
                            f"Today's Attendance: ",
                            font_weight="medium",
                        ),
                        rx.badge(
                            "Marked" if FacultyDashboardState.today_attendance_marked else "Pending",
                            color_scheme=(
                                "green" if FacultyDashboardState.today_attendance_marked
                                else "yellow"
                            ),
                            variant="solid",
                            font_size="1.25rem",
                        ),
                        spacing="2",
                        width="100%",
                        align_items="center",
                    ),
                    rx.button(
                        "Mark Today's Attendance",
                        on_click=FacultyDashboardState.mark_todays_attendance,
                        background_color="#2563eb",
                        color="white",
                        _hover={"background_color": "#1d4ed8"},
                        width="100%",
                    ),
                ),
            ),
            spacing="4",
            width="100%",
        ),
        width="100%",
        box_shadow="sm",
    )


def faculty_notices() -> rx.Component:
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
        FacultyDashboardState.notices_loading,
        rx.center(rx.spinner(size="3"), height="100px"),
        rx.cond(
            FacultyDashboardState.notices_error != "",
            rx.alert(
                rx.alert_icon(),
                rx.alert_title("Error"),
                rx.alert_description(FacultyDashboardState.notices_error),
                status="error",
            ),
            rx.cond(
                FacultyDashboardState.recent_notices.length() > 0,
                rx.vstack(
                    rx.foreach(
                        FacultyDashboardState.recent_notices,
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


def class_item(class_info: dict) -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.vstack(
                rx.text(class_info.get("subject", "Unknown Subject"), font_weight="medium"),
                rx.text(f"Time: {class_info.get('time', 'TBD')}", font_size="0.75rem", color="gray.500"),
                rx.text(f"Room: {class_info.get('room', 'TBD')}", font_size="0.75rem", color="gray.500"),
                rx.text(f"Type: {class_info.get('type', 'Class')}", font_size="0.75rem", color="gray.500"),
                spacing="1",
            ),
            rx.spacer(),
            rx.button(
                "Take Attendance",
                on_click=rx.alert("Attendance feature coming soon!"),
                variant="outline",
                size="2",
            ),
            width="100%",
            align_items="start",
        ),
        rx.divider(),
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