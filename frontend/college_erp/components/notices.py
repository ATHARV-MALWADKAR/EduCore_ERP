import reflex as rx
from college_erp.state.auth_state import AuthState
from college_erp.state.notices_state import NoticesState


def notices_list() -> rx.Component:
    return rx.cond(
        NoticesState.loading,
        rx.center(rx.spinner(size="3"), height="200px"),
        rx.cond(
            NoticesState.error != "",
            rx.alert(
                rx.alert_icon(),
                rx.alert_title("Error"),
                rx.alert_description(NoticesState.error),
                status="error",
                margin_bottom="1rem",
            ),
            rx.vstack(
                rx.cond(
                    AuthState.role.in_(["admin", "faculty"]),
                    rx.hstack(
                        rx.heading("All Notices", size="md"),
                        rx.spacer(),
                        rx.button(
                            "Refresh",
                            on_click=NoticesState.refresh_notices,
                            size="2",
                            variant="outline",
                        ),
                        width="100%",
                        align_items="center",
                    ),
                    rx.heading("Recent Notices", size="md"),
                ),
                rx.cond(
                    NoticesState.notices.length() > 0,
                    rx.vstack(
                        rx.foreach(
                            NoticesState.notices,
                            lambda notice: notice_card(notice)
                        ),
                        spacing="4",
                        width="100%",
                    ),
                    rx.center(
                        rx.vstack(
                            rx.icon("bell", size=48, color="gray.400"),
                            rx.text("No notices found", color="gray.500"),
                            spacing="2",
                        ),
                        padding="3rem",
                        text_align="center",
                    ),
                ),
                spacing="4",
                width="100%",
            ),
        ),
    )


def notice_card(notice: dict) -> rx.Component:
    # Format dates
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

    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.heading(notice.get("title", "Untitled Notice"), size="md"),
                    rx.hstack(
                        rx.badge(
                            notice.get("target_audience", "all").title(),
                            color_scheme=audience_color,
                            variant="soft",
                            font_size="0.75rem",
                        ),
                        rx.cond(
                            notice.get("department_name"),
                            rx.badge(
                                notice["department_name"],
                                color_scheme="gray",
                                variant="soft",
                                font_size="0.75rem",
                            ),
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
                    width="100%",
                ),
                rx.spacer(),
                rx.cond(
                    AuthState.role == notice.get("created_by_id"),
                    rx.hstack(
                        rx.button(
                            "Edit",
                            on_click=lambda: rx.redirect(
                                f"/notices/{notice.get('id')}/edit"
                            ),
                            background_color="#6b7280",
                            color="white",
                            _hover={"background_color": "#4b5563"},
                            size="2",
                        ),
                        rx.button(
                            "Delete",
                            on_click=lambda: NoticesState.delete_notice(notice.get("id")),
                            background_color="#ef4444",
                            color="white",
                            _hover={"background_color": "#dc2626"},
                            size="2",
                        ),
                        spacing="2",
                    ),
                ),
                width="100%",
                align_items="start",
            ),
            rx.text(
                notice.get("content", "No content available"),
                color="gray.600",
                font_size="0.875rem",
                line_height="1.6",
            ),
            spacing="4",
            width="100%",
        ),
        width="100%",
        box_shadow="sm",
    )


def create_notice_form() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.heading("Create New Notice", size="lg"),
                rx.spacer(),
                rx.button(
                    rx.icon("x", size=20),
                    on_click=NoticesState.toggle_create_form,
                    color_scheme="red",
                    variant="ghost",
                    size="2",
                ),
                width="100%",
                align_items="center",
            ),
            rx.form(
                rx.vstack(
                    rx.grid(
                        rx.vstack(
                            rx.label("Title", font_weight="medium"),
                            rx.input(
                                placeholder="Enter notice title",
                                value=NoticesState.title,
                                on_change=NoticesState.set_title,
                                required=True,
                                width="100%",
                            ),
                        ),
                        rx.vstack(
                            rx.label("Target Audience", font_weight="medium"),
                            rx.select(
                                items=[
                                    rx.option("All Users", value="all"),
                                    rx.option("Students Only", value="students"),
                                    rx.option("Faculty Only", value="faculty"),
                                ],
                                value=NoticesState.target_audience,
                                on_change=NoticesState.set_target_audience,
                                required=True,
                                width="100%",
                            ),
                        ),
                        template_columns="repeat(auto-fit, minmax(250px, 1fr))",
                        gap="1.5rem",
                        width="100%",
                    ),
                    rx.vstack(
                        rx.label("Content", font_weight="medium"),
                        rx.text_area(
                            placeholder="Enter notice content",
                            value=NoticesState.content,
                            on_change=NoticesState.set_content,
                            rows="6",
                            required=True,
                            width="100%",
                        ),
                    ),
                    rx.cond(
                        AuthState.role.in_(["admin", "faculty"]),
                        rx.vstack(
                            rx.label("Department (Optional)", font_weight="medium"),
                            rx.select(
                                items=[
                                    rx.option("All Departments", value=""),
                                    *[
                                        rx.option(
                                            f"{dept['name']} ({dept['code']})",
                                            value=str(dept["id"])
                                        )
                                        for dept in NoticesState.departments
                                    ]
                                ],
                                value=NoticesState.department_id,
                                on_change=NoticesState.set_department_id,
                                width="100%",
                            ),
                        ),
                    ),
                    rx.divider(),
                    rx.hstack(
                        rx.button(
                            "Cancel",
                            on_click=NoticesState.toggle_create_form,
                            variant="outline",
                            color_scheme="gray",
                        ),
                        rx.spacer(),
                        rx.button(
                            "Create Notice",
                            type="submit",
                            background_color="#2563eb",
                            color="white",
                            _hover={"background_color": "#1d4ed8"},
                            is_loading=NoticesState.loading,
                        ),
                        width="100%",
                        align_items="center",
                    ),
                    spacing="4",
                    width="100%",
                ),
                on_submit=NoticesState.create_notice,
                reset_on_submit=False,
                width="100%",
            ),
            spacing="4",
            width="100%",
        ),
        width="100%",
    )