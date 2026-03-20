from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str = "student"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=6)
    role: str = Field(..., pattern="^(student|faculty|admin)$")


class UserWithRole(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    is_active: bool = True

    class Config:
        from_attributes = True
