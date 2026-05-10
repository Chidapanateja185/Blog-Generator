import requests

from pydantic import BaseModel
from typing import Dict, Any

from jinja2 import (
    Environment,
    FileSystemLoader,
    TemplateNotFound
)

from src.utlis.utils import get_env_value


class EmailPayload(BaseModel):
    email_type: str
    to_email: str
    subject: str
    payload: Dict[str, Any]


class EmailService:

    def __init__(self):

        self.api_key = get_env_value(
            "RESEND_API_KEY"
        )

        self.from_email = get_env_value(
            "FROM_EMAIL"
        )

        self.template_env = Environment(
            loader=FileSystemLoader(
                "src/services/templates"
            )
        )

    async def send_email(
        self,
        email_payload: EmailPayload
    ):

        try:

            # Load HTML template
            template = self.template_env.get_template(
                f"{email_payload.email_type}.html"
            )

            # Render HTML
            html_content = template.render(
                **email_payload.payload
            )

            # Resend API request
            response = requests.post(

                "https://api.resend.com/emails",

                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },

                json={

                    "from": self.from_email,

                    "to": [email_payload.to_email],

                    "subject": email_payload.subject,

                    "html": html_content,
                }
            )

            # Debug response
            print(
                "Resend Response:",
                response.status_code,
                response.text
            )

            if response.status_code in [200, 201]:

                return {
                    "success": True,
                    "response": response.json()
                }

            return {
                "success": False,
                "error": response.text
            }

        except TemplateNotFound:

            print(
                f"Template "
                f"{email_payload.email_type}.html "
                f"not found"
            )

            return {
                "success": False,
                "error": "Template not found"
            }

        except Exception as e:

            print(
                f"Email Sending Failed: "
                f"{str(e)}"
            )

            return {
                "success": False,
                "error": str(e)
            }