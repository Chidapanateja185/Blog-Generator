from fastapi import APIRouter, Depends
from src.router.modules.auth_router import router as auth_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["auth"])

# router = APIRouter(
#     prefix="/user",
#     tags=["user"],
#     dependencies=[Depends(get_current_user)]
# )
