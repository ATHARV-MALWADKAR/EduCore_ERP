import reflex as rx

from college_erp.pages import index  # noqa: F401


def create_app() -> rx.App:
    app = rx.App()
    return app


app = create_app()
