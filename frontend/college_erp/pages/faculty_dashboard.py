import reflex as rx
from college_erp.state.auth_state import AuthState
from college_erp.state.faculty_dashboard_state import FacultyDashboardState
from college_erp.components.faculty_dashboard import (
    todays_classes,
    assignments_to_review,
    attendance_management,
    faculty_notices
)


@rx.page(route="/faculty/dashboard", title="Faculty Dashboard - College ERP")
def faculty_dashboard() -> rx.Component:
    return rx.box(
        rx.cond(
            AuthState.is_authenticated,
            rx.vstack(
                rx.hstack(
                    rx.heading("Faculty Dashboard", size="lg"),
                    rx.spacer(),
                    rx.badge(
                        f"Welcome, {AuthState.full_name}",
                        color_scheme="green",
                        variant="soft",
                    ),
                    width="100%",
                    align_items="center",
                ),
                rx.grid(
                    todays_classes(),
                    assignments_to_review(),
                    attendance_management(),
                    faculty_notices(),
                    template_columns="repeat(2, minmax(0, 1fr))",
                    gap="1.5rem",
                    width="100%",
                ),
                spacing="1.5rem",
                align_items="stretch",
                width="100%",
                max_width="1200px",
                margin_x="auto",
                padding="1.5rem",
            ),
            rx.center(
                rx.vstack(
                    rx.text("Please login to access dashboard", color="gray.600"),
                    rx.button(
                        "Login",
                        on_click=rx.redirect("/"),
                        background_color="#2563eb",
                        color="white",
                    ),
                    spacing="3",
                ),
                height="80vh",
            ),
        ),
        background_color="#f7fafc",
        min_height="100vh",
    )