import reflex as rx
from college_erp.state.auth_state import AuthState


def navbar() -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.hstack(
                rx.text("College ERP", font_size="1.5rem", font_weight="bold"),
                rx.spacer(),
                rx.cond(
                    AuthState.is_authenticated,
                    rx.hstack(
                        rx.text(
                            f"Hello, {AuthState.full_name}!",
                            font_size="0.875rem",
                            color="gray.600",
                        ),
                        rx.badge(
                            AuthState.role.title(),
                            color_scheme=(
                                "blue" if AuthState.role == "admin"
                                else "green" if AuthState.role == "faculty"
                                else "purple"
                            ),
                            variant="soft",
                            font_size="0.75rem",
                        ),
                        spacing="2",
                        align_items="center",
                    ),
                    rx.hstack(
                        rx.link("Login", href="/", font_size="0.875rem"),
                        rx.link("Register", href="/register", font_size="0.875rem"),
                        spacing="3",
                    ),
                ),
                align_items="center",
            ),
            rx.hstack(
                rx.cond(
                    AuthState.is_authenticated,
                    rx.hstack(
                        rx.link(
                            "Dashboard",
                            href=rx.cond(
                                AuthState.role == "admin",
                                "/admin/dashboard",
                                rx.cond(
                                    AuthState.role == "faculty",
                                    "/faculty/dashboard",
                                    "/student/dashboard"
                                )
                            ),
                            font_size="0.875rem",
                        ),
                        rx.link(
                            "Assignments",
                            href="/assignments",
                            font_size="0.875rem",
                        ),
                        rx.link(
                            "Notices",
                            href="/notices",
                            font_size="0.875rem",
                        ),
                        rx.link(
                            "Logout",
                            on_click=AuthState.logout,
                            font_size="0.875rem",
                            color="#ef4444",
                            _hover={"color": "#dc2626"},
                        ),
                        spacing="4",
                    ),
                    rx.hstack(
                        rx.link("Login", href="/", font_size="0.875rem"),
                        spacing="3",
                    ),
                ),
                align_items="center",
            ),
            justify="between",
            width="100%",
            padding="1rem",
            background_color="white",
            border_bottom="1px solid #e2e8f0",
        ),
        width="100%",
    )