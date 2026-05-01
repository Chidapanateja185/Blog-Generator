from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.schemas.auth import RegisterRequest, LoginRequest
from src.services.auth_service import AuthenticationService
from src.core.database import get_db
from src.utlis.dependencies import get_current_user, RefreshTokenBearer


router = APIRouter()


@router.post("/register")
async def signup(signup_req: RegisterRequest, db: Session = Depends(get_db)):
    auth_service = AuthenticationService(db)
    return await auth_service.register_user(signup_req)

@router.post("/login")
async def login(login_req: LoginRequest, db: Session = Depends(get_db)):
    auth_service = AuthenticationService(db)
    return await auth_service.login_user(login_req)

@router.post("/refresh")
async def refresh_token(token_data: dict = Depends(RefreshTokenBearer()),db: Session = Depends(get_db)):
    auth_service = AuthenticationService(db)
    return await auth_service.refresh_access_token(token_data)

@router.post("/logout")
async def logout(current_user=Depends(get_current_user),db: Session = Depends(get_db)):
    auth_service = AuthenticationService(db)
    return await auth_service.logout(current_user.id)