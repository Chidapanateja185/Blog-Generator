from firebase_admin import messaging
from pydantic import BaseModel


class SaveFCMTokenRequest(BaseModel):
    fcm_token: str


class PushNotificationService:

    async def send_notification(self, token: str, title: str, body: str):
        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                token=token
            )
            response = messaging.send(message)

            print(f"Notification sent: "f"{response}")
            return {
                "success": True,
                "response": response
            }

        except Exception as e:
            print(f"Notification Error: "f"{str(e)}")
            return {
                "success": False,
                "error": str(e)
            }