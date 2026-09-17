import reflex as rx
from college_erp.state.auth_state import AuthState
from college_erp.state.student_dashboard_state import StudentDashboardState
from college_erp.components.student_dashboard import (
    attendance_overview,
    assignments_overview,
    results_overview,
    notices_overview
)


@rx.page(route="/student/dashboard", title="Student Dashboard - College ERP")
def student_dashboard() -> rx.Component:
    return rx.box(
        rx.cond(
            AuthState.is_authenticated,
            rx.vstack(
                rx.hstack(
                    rx.heading("Student Dashboard", size="lg"),
                    rx.spacer(),
                    rx.badge(
                        f"Welcome, {AuthState.full_name}",
                        color_scheme="purple",
                        variant="soft",
                    ),
                    width="100%",
                    align_items="center",
                ),
                rx.grid(
                    attendance_overview(),
                    assignments_overview(),
                    results_overview(),
                    notices_overview(),
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