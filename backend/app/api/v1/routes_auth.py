from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse

from sqlalchemy.orm import Session

from app.core.deps import CurrentUser
from app.core.security import create_access_token, verify_password
from app.crud.user import create_user, get_user_by_email, get_role_by_name
from app.db.session import get_db
from app.schemas.auth import LoginRequest, RegisterRequest, Token, UserWithRole

router = APIRouter()


def _user_to_response(user) -> UserWithRole:
    return UserWithRole(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role.name,
        is_active=user.is_active,
    )


@router.post("/auth/login", response_model=Token)
def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Token:
    """
    Login with email and password. Send as form: username=email, password=password.
    Returns JWT access token for use in Authorization: Bearer <token>.
    """
    user = get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )
    access_token = create_access_token(
        subject=user.email,
        user_id=user.id,
        role_name=user.role.name,
    )
    return Token(
        access_token=access_token,
        token_type="bearer",
        role=user.role.name,
    )


@router.post("/auth/login/json", response_model=Token)
def login_json(
    data: LoginRequest,
    db: Session = Depends(get_db),
) -> JSONResponse:
    """Login with JSON body (email, password). Returns JWT access token."""
    user = get_user_by_email(db, data.email)
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )
    access_token = create_access_token(
        subject=user.email,
        user_id=user.id,
        role_name=user.role.name,
    )
    
    # Create response with token
    response_data = {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role.name,
    }
    
    # Create JSONResponse to set cookie
    response = JSONResponse(content=response_data)
    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=60 * 60,  # 1 hour
        secure=False,  # Set to True in production with HTTPS
        httponly=True,
        samesite="lax",
    )
    return response


@router.post("/auth/register", response_model=UserWithRole)
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db),
) -> UserWithRole:
    """
    Register a new user with role: student, faculty, or admin.
    """
    if get_user_by_email(db, data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    role = get_role_by_name(db, data.role)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role; use one of: student, faculty, admin",
        )
    try:
        user = create_user(
            db,
            email=data.email,
            full_name=data.full_name,
            password=data.password,
            role_name=data.role,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    return _user_to_response(user)


@router.get("/auth/me", response_model=UserWithRole)
def me(current_user: CurrentUser) -> UserWithRole:
    """Return current authenticated user. Requires Bearer token."""
    return _user_to_response(current_user)


@router.post("/auth/logout")
def logout():
    """Logout endpoint - clears the session."""
    response = JSONResponse({"message": "Logged out successfully"})
    response.delete_cookie("access_token")
    return response
