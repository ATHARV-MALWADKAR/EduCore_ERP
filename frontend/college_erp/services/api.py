import httpx
import os
from typing import Optional, Dict, Any, List

API_BASE_URL = os.environ.get("API_URL", "http://localhost:8000/api/v1")


class APIClient:
    """Client for communicating with the College ERP backend."""

    def __init__(self):
        self._token = None

    def set_token(self, token: str):
        self._token = token

    def clear_token(self):
        self._token = None

    @property
    def headers(self) -> Dict[str, str]:
        if self._token:
            return {"Authorization": f"Bearer {self._token}"}
        return {}

    async def _request(
        self, method: str, endpoint: str, **kwargs
    ) -> Dict[str, Any]:
        """Make an async HTTP request to the API."""
        url = f"{API_BASE_URL}{endpoint}"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(
                    method, url, headers=self.headers, **kwargs
                )
                response.raise_for_status()
                # 204 No Content has no JSON
                if response.status_code == 204:
                    return {}
                return response.json()
            except httpx.HTTPStatusError as e:
                # Try to extract the detail message from the FastAPI error response
                try:
                    error_msg = e.response.json().get("detail", str(e))
                except Exception:
                    error_msg = str(e)
                raise Exception(f"API Error: {error_msg}")
            except Exception as e:
                raise Exception(f"Connection Error: {str(e)}")


    # --- Auth ---
    async def login(self, email: str, password: str) -> Dict[str, Any]:
        data = {"username": email, "password": password}
        response = await self._request("POST", "/auth/login", data=data)
        if "access_token" in response:
            self.set_token(response["access_token"])
        return response

    async def get_me(self) -> Dict[str, Any]:
        return await self._request("GET", "/auth/me")

    # --- Admin Dashboards ---
    async def get_departments(self) -> Dict[str, Any]:
        return await self._request("GET", "/admin/departments")

    async def get_courses(self) -> Dict[str, Any]:
        return await self._request("GET", "/admin/courses")

    async def get_users(self, role: str = None) -> Dict[str, Any]:
        params = {"role": role} if role else {}
        return await self._request("GET", "/admin/users", params=params)

    # --- Student Dashboards ---
    async def get_student_profile(self, student_id: int) -> Dict[str, Any]:
        return await self._request("GET", f"/students/{student_id}")

    # --- Faculty / Attendance ---
    async def get_attendance_report(self) -> Dict[str, Any]:
        return await self._request("GET", "/attendance/report/overall")

    async def get_student_attendance(self, student_id: int) -> Dict[str, Any]:
        return await self._request("GET", f"/attendance/summary/student/{student_id}")


# Global singleton instance
api = APIClient()
