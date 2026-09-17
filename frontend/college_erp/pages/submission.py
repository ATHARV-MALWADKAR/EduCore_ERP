import reflex as rx
from college_erp.services.api import api
from college_erp.state.auth_state import AuthState
from college_erp.state.submission_state import SubmissionState
from college_erp.components.submission import submission_details, submission_grading_form


@rx.page(route="/submissions/[assignment_id]", title="Submission Details - College ERP")
def submission_details_page() -> rx.Component:
    assignment_id = rx.State.router.page.params.get("assignment_id", "0")

    return rx.box(
        rx.cond(
            AuthState.is_authenticated,
            rx.vstack(
                rx.heading("Submission Details", size="lg"),
                rx.button(
                    "Back to Assignments",
                    on_click=rx.redirect("/assignments"),
                    background_color="#6b7280",
                    color="white",
                    _hover={"background_color": "#4b5563"},
                    margin_bottom="2rem",
                ),
                rx.cond(
                    AuthState.role == "faculty",
                    rx.vstack(
                        rx.heading("Grade Submission", size="md"),
                        rx.cond(
                            SubmissionState.is_loading,
                            rx.spinner(size="3"),
                            submission_grading_form(int(assignment_id))
                        ),
                        margin_bottom="2rem",
                    ),
                    rx.box(),
                ),
                submission_details(int(assignment_id)),
                spacing="4",
                width="100%",
                max_width="1200px",
                margin_x="auto",
                padding="2rem",
            ),
            rx.center(
                rx.vstack(
                    rx.text("Please login to access submission details", color="gray.600"),
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