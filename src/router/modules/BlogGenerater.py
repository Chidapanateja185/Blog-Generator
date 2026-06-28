from fastapi import APIRouter
from urllib3 import request
from src.services.BlogGenerationService import BlogGenerationService, BlogGenerationRequest, BlogGenerationResponse

router = APIRouter()
service = BlogGenerationService()

@router.post("/generate_blog")
async def generate_blog(request: BlogGenerationRequest):
    response = await service.generate_blog(request)
    return response