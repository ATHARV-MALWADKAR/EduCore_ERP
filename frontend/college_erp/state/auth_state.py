import reflex as rx
from college_erp.services.api import api

class AuthState(rx.State):
    is_authenticated: bool = False
    role: str = ""
    user_id: int = 0
    full_name: str = ""
    access_token: str = ""
    error_message: str = ""
    is_loading: bool = False

    async def login(self, form_data: dict) -> None:
        """Handle login form submission."""
        self.is_loading = True
        self.error_message = ""
        yield

        try:
            email = form_data.get("email")
            password = form_data.get("password")

            response = await api.login(email, password)

            self.is_authenticated = True
            self.access_token = response["access_token"]
            self.role = response["role"]
            self.user_id = response["user_id"]
            self.full_name = response["full_name"]

            # Redirect to the correct dashboard based on role
            if self.role == "admin":
                yield rx.redirect("/admin/dashboard")
            elif self.role == "faculty":
                yield rx.redirect("/faculty/dashboard")
            elif self.role == "student":
                yield rx.redirect("/student/dashboard")

        except Exception as e:
            self.error_message = str(e)
        finally:
            self.is_loading = False
            yield

    def logout(self) -> None:
        """Handle logout."""
        self.is_authenticated = False
        self.role = ""
        self.user_id = 0
        self.full_name = ""
        self.access_token = ""
        api.clear_token()
        return rx.redirect("/")

