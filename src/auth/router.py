from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.user.exceptions import EmailAlreadyRegistered, EmailNotFound, PasswordNotValid
from src.core.database import get_db
from src.auth.service import AuthService
from src.user.schemas import UserLogin, UserCreate
from src.session.schemas import SessionRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
async def register(
    user: UserCreate,
    db: AsyncSession = Depends(get_db)
) -> dict:
    service = AuthService(db)
    try:
        await service.register_user(user)
    except EmailAlreadyRegistered:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered.")
    return {"message": "Registered successfully. Now you need confirm your email and login."}


@router.post("/login")
async def login(
    user: UserLogin,
    response: Response,
    db: AsyncSession = Depends(get_db)
) -> dict:
    service = AuthService(db)
    try:
        session = await service.login_user(user)
    except EmailNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email not found")
    except PasswordNotValid:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Password not valid")
    response.set_cookie(
        key="session_token",
        value=session.session_token,
        httponly=True,
        secure=False, # True in production
        samesite="lax",
        max_age=60 * 60 * 24 * 30 # 1 month
    )
    return {"message": "Logged in"}



@router.post("/logout")
async def logout(
    response: Response,
    session_token: str,
    db: AsyncSession = Depends(get_db)
):
    service = AuthService(db)
    success = await service.logout_user(session_token)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session"
        )
    
    response.delete_cookie("session_token")
    return {"message": "Logout seccessfully"}


@router.get("/confirm-email")
async def confirm_email(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    service = AuthService(db)
    success = await service.confirm_email(token)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session"
        )
    return {"message": "Confirmed seccessfully"}
        

    
    