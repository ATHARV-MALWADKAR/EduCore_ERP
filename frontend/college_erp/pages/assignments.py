import reflex as rx
from college_erp.services.api import api
from college_erp.state.auth_state import AuthState
from college_erp.state.assignments_state import AssignmentsState
from college_erp.components.assignments import assignment_list, create_assignment_form


@rx.page(route="/assignments", title="Assignments - College ERP")
def assignments() -> rx.Component:
    return rx.box(
        rx.cond(
            AuthState.is_authenticated,
            rx.vstack(
                rx.heading("Assignments Management", size="lg"),
                rx.cond(
                    AuthState.role == "faculty",
                    rx.vstack(
                        rx.button(
                            "Create New Assignment",
                            on_click=AssignmentsState.toggle_create_form,
                            background_color="#2563eb",
                            color="white",
                            _hover={"background_color": "#1d4ed8"},
                            margin_bottom="1rem",
                        ),
                        rx.cond(
                            AssignmentsState.show_create_form,
                            create_assignment_form(),
                        ),
                        margin_bottom="2rem",
                    ),
                    rx.box(),
                ),
                assignment_list(),
                spacing="4",
                width="100%",
                max_width="1200px",
                margin_x="auto",
                padding="2rem",
            ),
            rx.center(
                rx.vstack(
                    rx.text("Please login to access assignments", color="gray.600"),
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