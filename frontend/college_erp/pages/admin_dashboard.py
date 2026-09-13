import reflex as rx
from typing import List, Dict, Any
from college_erp.components.layouts import dashboard_layout
from college_erp.services.api import api
from college_erp.state.auth_state import AuthState


class AdminState(rx.State):
    departments_count: int = 0
    courses_count: int = 0
    students_count: int = 0
    faculty_count: int = 0
    attendance_percentage: float = 0.0
    is_loading: bool = True

    async def load_data(self) -> None:
        """Fetch all dashboard metrics from the API."""
        self.is_loading = True
        yield

        try:
            depts = await api.get_departments()
            self.departments_count = depts.get("meta", {}).get("total", 0)

            courses = await api.get_courses()
            self.courses_count = courses.get("meta", {}).get("total", 0)

            students = await api.get_users(role="student")
            self.students_count = students.get("meta", {}).get("total", 0)

            faculty = await api.get_users(role="faculty")
            self.faculty_count = faculty.get("meta", {}).get("total", 0)

            att = await api.get_attendance_report()
            self.attendance_percentage = att.get("attendance_percentage", 0.0)

        except Exception as e:
            print(f"Error loading admin dashboard: {e}")
        finally:
            self.is_loading = False
            yield


@rx.page(route="/admin/dashboard", title="Admin Dashboard", on_load=AdminState.load_data)
def admin_dashboard() -> rx.Component:
    return dashboard_layout(
        rx.vstack(
            rx.hstack(
                rx.heading("Administrator Dashboard", size="lg"),
                rx.spacer(),
                rx.button("Logout", on_click=AuthState.logout, color_scheme="red", size="sm"),
                width="100%",
                align_items="center"
            ),
            rx.text("Live overview of university departments, operations, and demographics."),
            rx.grid(
                rx.box(
                    rx.heading(f"{AdminState.students_count}", size="xl", color="#2563eb"),
                    rx.text("Total Students", font_weight="bold"),
                    padding="1.5rem",
                    border_radius="md",
                    background_color="white",
                    box_shadow="md",
                ),
                rx.box(
                    rx.heading(f"{AdminState.faculty_count}", size="xl", color="#059669"),
                    rx.text("Faculty Members", font_weight="bold"),
                    padding="1.5rem",
                    border_radius="md",
                    background_color="white",
                    box_shadow="md",
                ),
                rx.box(
                    rx.heading(f"{AdminState.departments_count}", size="xl", color="#d97706"),
                    rx.text("Academic Departments", font_weight="bold"),
                    padding="1.5rem",
                    border_radius="md",
                    background_color="white",
                    box_shadow="md",
                ),
                rx.box(
                    rx.heading(f"{AdminState.attendance_percentage}%", size="xl", color="#7c3aed"),
                    rx.text("Average Attendance", font_weight="bold"),
                    padding="1.5rem",
                    border_radius="md",
                    background_color="white",
                    box_shadow="md",
                ),
                template_columns="repeat(4, minmax(0, 1fr))",
                gap="1.5rem",
                width="100%",
            ),
            spacing="1.5rem",
            align_items="stretch",
            width="100%",
        )
    )
