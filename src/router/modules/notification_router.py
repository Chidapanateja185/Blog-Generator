from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session
from src.core.database import get_db
from src.models.users import Users
from src.utlis.dependencies import (get_current_user)
from src.services.notification_service import SaveFCMTokenRequest

router = APIRouter()

@router.post("/save-token")
async def save_fcm_token(payload: SaveFCMTokenRequest,db: Session = Depends(get_db),current_user: Users = Depends(get_current_user)):

    current_user.fcm_token = (payload.fcm_token)
    db.commit()
    return {
        "success": True,
        "message": "FCM token saved"
    }