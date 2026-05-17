import requests
import os
from pydantic import BaseModel
from typing import Dict, Any
from dotenv import load_dotenv
from jinja2 import (
    Environment,
    FileSystemLoader,
    TemplateNotFound
)

from src.utlis.utils import get_env_value

load_dotenv()

class EmailPayload(BaseModel):
    email_type: str
    to_email: str
    subject: str
    payload: Dict[str, Any]


class EmailService:

    def __init__(self):
        
        # self.api_key = get_env_value("BREVO_API_KEY", os.getenv("BREVO_API_KEY"))
        # self.from_email = get_env_value("FROM_EMAIL", os.getenv("FROM_EMAIL"))
        
        self.api_key = os.getenv("BREVO_API_KEY")
        self.from_email = os.getenv("FROM_EMAIL")

        self.template_env = Environment(
            loader=FileSystemLoader(
                "src/services/templates"
            )
        )

    async def send_email(self, email_payload: EmailPayload):

        try:
            # Load template
            template = self.template_env.get_template(
                f"{email_payload.email_type}.html"
            )

            # Render HTML
            html_content = template.render(**email_payload.payload)
            
            print("BREVO_API_KEY:", self.api_key)
            print("FROM_EMAIL:", self.from_email)

            # Brevo API request
            response = requests.post(

                "https://api.brevo.com/v3/smtp/email",
                headers={
                    "accept": "application/json",
                    "api-key": self.api_key,
                    "content-type": "application/json"
                },

                json={
                    "sender": {
                        "name": "BlogCraft",
                        "email": self.from_email
                    },
                    "to": [
                        {"email": email_payload.to_email}
                    ],
                    "subject": email_payload.subject,
                    "htmlContent": html_content
                }
            )
            print("Brevo Response:", response.status_code, response.text)

            if response.status_code in [200, 201, 202]:
                return {
                    "success": True,
                    "response": response.json()
                }
            return {
                "success": False,
                "error": response.text
            }

        except TemplateNotFound:
            print(f"Template {email_payload.email_type}.html not found")
            return {
                "success": False,
                "error": "Template not found"
            }
        except Exception as e:
            print(f"Email Sending Failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }