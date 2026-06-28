from fastapi import APIRouter, Depends
from src.router.modules.auth_router import router as auth_router
from src.router.modules.notification_router import router as notification_router
from src.router.modules.BlogGenerater import router as blog_generator_router


api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(notification_router, prefix="/notification", tags=["notification"])
api_router.include_router(blog_generator_router, prefix="/blog", tags=["blog"])

# router = APIRouter(
#     prefix="/user",
#     tags=["user"],
#     dependencies=[Depends(get_current_user)]
# )
