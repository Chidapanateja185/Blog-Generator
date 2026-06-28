import os
import json
from typing import List, Optional

from google import genai
from google.genai import types
from pydantic import BaseModel


class BlogGenerationRequest(BaseModel):
    title: str
    category: str
    tone: str
    notes: Optional[str] = None


class BlogGenerationResponse(BaseModel):
    title: str
    meta_description: str
    tags: List[str]
    content: str


class BlogGenerationService:

    def __init__(self):
        api_key = os.getenv("GENAI_API_KEY")

        if not api_key:
            raise RuntimeError("GENAI_API_KEY is missing.")

        self.client = genai.Client(api_key=api_key)

    async def generate_blog(self, request: BlogGenerationRequest):

        prompt = f"""
            Generate a professional SEO blog.

            Title: {request.title}
            Category: {request.category}
            Tone: {request.tone}
            Notes: {request.notes or "None"}

            Requirements:
            1. SEO optimized.
            2. 1200-1800 words.
            3. Use headings and subheadings.
            4. Include a conclusion.
            5. Include actionable insights.

            Return ONLY JSON.
            """

        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=BlogGenerationResponse,
            ),
        )

        
        try:
            blog_json = json.loads(response.text)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Gemini did not return valid JSON.\nResponse:\n{response.text}"
            ) from e

        return BlogGenerationResponse(**blog_json)