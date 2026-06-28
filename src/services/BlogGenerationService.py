import os
import json
import time
import logging
from typing import List, Optional

from google import genai
from google.genai import types
from pydantic import BaseModel


logger = logging.getLogger(__name__)


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

        logger.info("Initializing BlogGenerationService...")

        self.api_key = os.getenv("GENAI_API_KEY")

        if not self.api_key:
            logger.error("GENAI_API_KEY not found in environment variables.")
            raise RuntimeError("GENAI_API_KEY is missing.")

        logger.info("GENAI_API_KEY found successfully.")

        self.client = genai.Client(api_key=self.api_key)

        logger.info("Gemini client initialized successfully.")

    async def generate_blog(
        self,
        request: BlogGenerationRequest
    ) -> BlogGenerationResponse:

        logger.info("Starting Blog Generation")

        logger.info("Title      : %s", request.title)
        logger.info("Category   : %s", request.category)
        logger.info("Tone       : %s", request.tone)
        logger.info("Notes      : %s", request.notes)

        prompt = f"""
            Generate a professional SEO blog.

            Title: {request.title}
            Category: {request.category}
            Tone: {request.tone}
            Notes: {request.notes or "None"}

            Requirements:

            1. SEO optimized.
            2. 1800-2000 words.
            3. Use headings and subheadings.
            4. Include conclusion.
            5. Include actionable insights.

            Return ONLY valid JSON.

            JSON Format:

            {{
                "title": "",
                "meta_description": "",
                "tags": [],
                "content": ""
            }}
            """

        logger.info("Prompt Length : %d characters", len(prompt))

        try:

            logger.info("Sending request to Gemini API...")

            start = time.time()

            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=BlogGenerationResponse,
                ),
            )

            end = time.time()

            logger.info(
                "Gemini API responded successfully in %.2f seconds",
                end - start,
            )

            logger.info(
                "Response Length : %d characters",
                len(response.text)
            )

            logger.debug("Raw Gemini Response:\n%s", response.text)

        except Exception:
            logger.exception("Error while calling Gemini API.")
            raise

        try:

            logger.info("Parsing JSON response...")

            blog_json = json.loads(response.text)

            logger.info("JSON parsed successfully.")

        except json.JSONDecodeError:

            logger.exception("Failed to parse Gemini JSON response.")

            logger.error("Raw Gemini Response:\n%s", response.text)

            raise ValueError(
                "Gemini did not return valid JSON."
            )

        try:

            logger.info("Building BlogGenerationResponse object...")

            blog = BlogGenerationResponse(**blog_json)

            logger.info("BlogGenerationResponse created successfully.")

            logger.info("Generated Blog Title : %s", blog.title)
            logger.info("Generated Tags       : %s", blog.tags)
            logger.info(
                "Content Length       : %d characters",
                len(blog.content),
            )

            logger.info("Blog Generation Completed Successfully")

            return blog

        except Exception:

            logger.exception(
                "Failed while constructing BlogGenerationResponse."
            )

            raise