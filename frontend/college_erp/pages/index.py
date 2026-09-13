import reflex as rx

from college_erp.components.layouts import dashboard_layout
from college_erp.state.auth_state import AuthState


@rx.page(route="/", title="College ERP - Login")
def index() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.heading("College ERP Login", size="lg", text_align="center", padding_bottom="1rem"),
            rx.cond(
                AuthState.error_message != "",
                rx.text(AuthState.error_message, color="red", font_size="0.875rem", font_weight="bold"),
            ),
            rx.form(
                rx.vstack(
                    rx.input(
                        placeholder="Email Address",
                        name="email",
                        type="email",
                        width="100%",
                        required=True,
                    ),
                    rx.input(
                        placeholder="Password",
                        name="password",
                        type="password",
                        width="100%",
                        required=True,
                    ),
                    rx.button(
                        "Sign In",
                        type="submit",
                        width="100%",
                        is_loading=AuthState.is_loading,
                        background_color="#2563eb",
                        color="white",
                        _hover={"background_color": "#1d4ed8"}
                    ),
                    spacing="4",
                    width="100%",
                ),
                on_submit=AuthState.login,
                reset_on_submit=False,
                width="100%",
            ),
            rx.divider(margin_y="1.5rem"),
            rx.text(
                "Demo Accounts:",
                font_weight="bold",
                font_size="0.875rem",
                color="gray.600"
            ),
            rx.text("Admin: admin@college.edu / admin123", font_size="0.75rem"),
            rx.text("Faculty: prof.alan@college.edu / faculty123", font_size="0.75rem"),
            rx.text("Student: student.john@college.edu / student123", font_size="0.75rem"),
            padding="2rem",
            background_color="white",
            border_radius="lg",
            box_shadow="lg",
            width=["90%", "400px"],
            align_items="center",
        ),
        width="100vw",
        height="100vh",
        background_color="#f3f4f6",
    )

