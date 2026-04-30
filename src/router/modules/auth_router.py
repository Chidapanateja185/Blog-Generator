from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.schemas.auth import RegisterRequest
from src.services.auth_service import AuthenticationService
from src.core.database import get_db

router = APIRouter()


@router.post("/register")
async def signup(signup_req: RegisterRequest, db: Session = Depends(get_db)):
    auth_service = AuthenticationService(db)
    return await auth_service.register_user(signup_req)  