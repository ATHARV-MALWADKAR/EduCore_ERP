import reflex as rx
from college_erp.services.api import api
from college_erp.state.auth_state import AuthState
from college_erp.state.notices_state import NoticesState
from college_erp.components.notices import notices_list, create_notice_form


@rx.page(route="/notices", title="Notices - College ERP")
def notices() -> rx.Component:
    return rx.box(
        rx.cond(
            AuthState.is_authenticated,
            rx.vstack(
                rx.heading("Notices & Announcements", size="lg"),
                rx.cond(
                    AuthState.role.in_(["admin", "faculty"]),
                    rx.vstack(
                        rx.button(
                            "Create New Notice",
                            on_click=NoticesState.toggle_create_form,
                            background_color="#2563eb",
                            color="white",
                            _hover={"background_color": "#1d4ed8"},
                            margin_bottom="1rem",
                        ),
                        rx.cond(
                            NoticesState.show_create_form,
                            create_notice_form(),
                        ),
                        margin_bottom="2rem",
                    ),
                    rx.box(),
                ),
                notices_list(),
                spacing="4",
                width="100%",
                max_width="1200px",
                margin_x="auto",
                padding="2rem",
            ),
            rx.center(
                rx.vstack(
                    rx.text("Please login to access notices", color="gray.600"),
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