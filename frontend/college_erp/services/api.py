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
        async with httpx.AsyncClient(timeout=30.0) as client:
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
    async def get_departments(self) -> List[Dict[str, Any]]:
        return await self._request("GET", "/admin/departments")

    async def get_courses(self) -> List[Dict[str, Any]]:
        return await self._request("GET", "/admin/courses")

    async def get_users(self, role: str = None) -> List[Dict[str, Any]]:
        params = {"role": role} if role else {}
        return await self._request("GET", "/admin/users", params=params)

    # --- Student Dashboards ---
    async def get_student_profile(self, student_id: int) -> Dict[str, Any]:
        return await self._request("GET", f"/students/{student_id}")

    async def get_faculty_profile(self, faculty_id: int) -> Dict[str, Any]:
        return await self._request("GET", f"/faculty/{faculty_id}")

    # --- Faculty / Attendance ---
    async def get_attendance_report(self) -> Dict[str, Any]:
        return await self._request("GET", "/attendance/report/overall")

    async def get_student_attendance(self, student_id: int) -> Dict[str, Any]:
        return await self._request("GET", f"/attendance/summary/student/{student_id}")

    async def get_assignments_by_faculty(self, faculty_id: int) -> List[Dict[str, Any]]:
        return await self._request("GET", f"/faculty/{faculty_id}/assignments")

    async def get_attendance_list(
        self, skip: int = 0, limit: int = 100, student_id: int = None, subject_id: int = None
    ) -> Dict[str, Any]:
        params = {"skip": skip, "limit": limit}
        if student_id:
            params["student_id"] = student_id
        if subject_id:
            params["subject_id"] = subject_id
        return await self._request("GET", "/attendance/", params=params)

    async def mark_attendance(
        self, student_id: int, subject_id: int, date: str, status: str, remarks: str = None
    ) -> Dict[str, Any]:
        data = {
            "student_id": student_id,
            "subject_id": subject_id,
            "date": date,
            "status": status,
        }
        if remarks:
            data["remarks"] = remarks
        return await self._request("POST", "/attendance/mark", json=data)

    # --- Assignments ---
    async def get_assignments(self, subject_id: int = None) -> List[Dict[str, Any]]:
        params = {}
        if subject_id:
            params["subject_id"] = subject_id
        return await self._request("GET", "/assignments", params=params)

    async def get_assignment(self, assignment_id: int) -> Dict[str, Any]:
        return await self._request("GET", f"/assignments/{assignment_id}")

    async def create_assignment(
        self, subject_id: int, title: str, description: str, due_at: str, status: str = "published"
    ) -> Dict[str, Any]:
        data = {
            "subject_id": subject_id,
            "title": title,
            "description": description,
            "due_at": due_at,
            "status": status,
            "created_by_id": 0  # Will be set by backend
        }
        return await self._request("POST", "/assignments", json=data)

    async def update_assignment(
        self, assignment_id: int, title: str = None, description: str = None,
        due_at: str = None, status: str = None
    ) -> Dict[str, Any]:
        data = {}
        if title:
            data["title"] = title
        if description:
            data["description"] = description
        if due_at:
            data["due_at"] = due_at
        if status:
            data["status"] = status
        return await self._request("PUT", f"/assignments/{assignment_id}", json=data)

    async def submit_assignment(
        self, assignment_id: int, content: str
    ) -> Dict[str, Any]:
        return await self._request(
            "POST",
            f"/assignments/{assignment_id}/submit",
            data={"content": content}
        )

    async def get_submissions(self, assignment_id: int) -> List[Dict[str, Any]]:
        return await self._request("GET", f"/assignments/{assignment_id}/submissions")

    async def grade_submission(
        self, submission_id: int, marks_given: float, feedback: str = None
    ) -> Dict[str, Any]:
        data = {"marks_given": marks_given}
        if feedback:
            data["feedback"] = feedback
        return await self._request("PUT", f"/submissions/{submission_id}/grade", json=data)

    # --- Notices ---
    async def get_notices(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        return await self._request("GET", "/notices", params={"skip": skip, "limit": limit})

    async def get_notice(self, notice_id: int) -> Dict[str, Any]:
        return await self._request("GET", f"/notices/{notice_id}")

    async def create_notice(
        self, title: str, content: str, target_audience: str = "all", department_id: int = None
    ) -> Dict[str, Any]:
        data = {
            "title": title,
            "content": content,
            "target_audience": target_audience,
            "created_by_id": 0  # Will be set by backend
        }
        if department_id:
            data["department_id"] = department_id
        return await self._request("POST", "/notices", json=data)

    async def update_notice(
        self, notice_id: int, title: str = None, content: str = None,
        target_audience: str = None, department_id: int = None
    ) -> Dict[str, Any]:
        data = {}
        if title:
            data["title"] = title
        if content:
            data["content"] = content
        if target_audience:
            data["target_audience"] = target_audience
        if department_id is not None:
            data["department_id"] = department_id
        return await self._request("PUT", f"/notices/{notice_id}", json=data)

    async def delete_notice(self, notice_id: int) -> Dict[str, Any]:
        return await self._request("DELETE", f"/notices/{notice_id}")

    # --- Timetable ---
    async def get_timetable(self, course_id: int = None, academic_year: str = None) -> List[Dict[str, Any]]:
        params = {}
        if course_id:
            params["course_id"] = course_id
        if academic_year:
            params["academic_year"] = academic_year
        return await self._request("GET", "/timetable", params=params)

    # --- Results ---
    async def get_results(self, student_id: int = None) -> List[Dict[str, Any]]:
        params = {}
        if student_id:
            params["student_id"] = student_id
        return await self._request("GET", "/results", params=params)

    async def create_result(
        self, student_id: int, subject_id: int, exam_type: str,
        academic_year: str, marks_obtained: float, max_marks: float, grade: str = None
    ) -> Dict[str, Any]:
        data = {
            "student_id": student_id,
            "subject_id": subject_id,
            "exam_type": exam_type,
            "academic_year": academic_year,
            "marks_obtained": marks_obtained,
            "max_marks": max_marks,
        }
        if grade:
            data["grade"] = grade
        return await self._request("POST", "/results", json=data)


# Global singleton instance
api = APIClient()
