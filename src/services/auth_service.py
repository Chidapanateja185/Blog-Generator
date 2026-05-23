from random import randint

from jose import JWTError, jwt
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from src.models.users import Users
from src.schemas.auth import LoginRequest, LoginResponse, RegisterRequest
from src.services.notification_service import PushNotificationService
from src.services.email_service import EmailPayload, EmailService
from src.core.security import (
    hashpassword,
    verify_password,
    create_access_token,
    create_refresh_token,
    create_password_reset_token,
    decode_token
)

class AuthenticationService:

    def __init__(self, db: Session):
        self.db = db

    async def register_user(self, req: RegisterRequest):

        if req.password != req.conform_password:
            return JSONResponse(status_code=400, content={"message": "Passwords do not match"})

        if self.db.query(Users).filter(Users.email == req.email).first():
            return JSONResponse(status_code=400, content={"message": "Email already exists"})

        if self.db.query(Users).filter(Users.mobile == req.mobile).first():
            return JSONResponse(status_code=400, content={"message": "Mobile already exists"})

        user = Users(
            firstName=req.first_name,
            lastName=req.last_name,
            email=req.email,
            mobile=req.mobile,
            password=hashpassword(req.password),
            role="USER",
            fcm_token=req.fcm_token
        )

        # Send an Email
        service = EmailService()
        response = await service.send_email(
            EmailPayload(
                email_type="welcome",
                to_email=req.email,
                subject="Welcome to BlogCraft!",
                payload={
                    "first_name": req.first_name,
                    "last_name": req.last_name,
                    "year": datetime.now().year
                }
            )
        )

        # Push Notification
        push_response = None
        if user.fcm_token:
            push_service = (PushNotificationService())
            push_response = await (
                push_service.send_notification(
                    token=user.fcm_token,
                    title="Welcome to BlogCraft 🎉",
                    body=(
                        "Your account was created successfully"
                    )
                )
            )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return {
            "message": "User created successfully",
            "data": {
                "id": user.id,
                "firstName": user.firstName,
                "lastName": user.lastName,
                "email": user.email,
                "mobile": user.mobile,
                "role": user.role,
                "Email sent status" : response.get("success"),
                "push_sent": push_response.get("success") if push_response else None
            }
        }


    async def login_user(self, login_req: LoginRequest) -> LoginResponse:

        user = self.db.query(Users).filter(
            Users.email == login_req.email
        ).first()

        if not user or not verify_password(login_req.password, user.password):
            return JSONResponse(
                status_code=401,
                content={"message": "Invalid email or password"}
            )

        payload = {
            "user_id": str(user.id),
            "email": user.email,
            "role": user.role.value,
            "firstName": user.firstName,
            "lastName": user.lastName
        }

        access_token = create_access_token(payload)
        refresh_token = create_refresh_token(payload)


        user.refresh_token = refresh_token
        self.db.commit()

        return LoginResponse(
            message="Login successful",
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )
    

    async def refresh_access_token(self, token_data: dict):

        try:
            if token_data.get("type") != "refresh":
                return JSONResponse(status_code=401, content={"message": "Invalid token"})

            user = self.db.query(Users).filter(
                Users.id == token_data.get("user_id")
            ).first()

            if not user:
                return JSONResponse(status_code=401, content={"message": "User not found"})

            if user.refresh_token != token_data.get("raw"):
                return JSONResponse(status_code=401, content={"message": "Token mismatch"})

            payload = {
                "user_id": str(user.id),
                "email": user.email,
                "role": user.role.value,
                "firstName": user.firstName,
                "lastName": user.lastName
            }

            new_access_token = create_access_token(payload)

            return {
                "access_token": new_access_token,
                "token_type": "bearer"
            }

        except JWTError:
            return JSONResponse(status_code=401, content={"message": "Invalid token"})

    async def logout(self, user_id):

        user = self.db.query(Users).filter(Users.id == user_id).first()

        if user:
            user.refresh_token = None
            self.db.commit()

        return {
            "Status code" : status.HTTP_200_OK,
            "message": "Logged out successfully"
        }
    
    async def send_email_otp(self, email: str):

        user = self.db.query(Users).filter(Users.email == email).first()

        if not user:
            return JSONResponse(status_code=401, content={"message": "User Email is not registered"})

        # Generate OTP and set expiry
        otp = str(randint(100000, 999999))
        user.email_otp = otp
        user.expires_at = datetime.utcnow() + timedelta(minutes=10)
        user.email_otp_created_at = datetime.utcnow()

        # Send OTP Email
        service = EmailService()
        response = await service.send_email(
            EmailPayload(
                email_type="verify_otp",
                to_email=email,
                subject="Your OTP To Reset the Password for BlogCraft",
                payload={
                    "first_name": user.firstName,
                    "user_email": user.email,
                    "D1": otp[0],
                    "D2": otp[1],
                    "D3": otp[2],
                    "D4": otp[3],
                    "D5": otp[4],
                    "D6": otp[5],
                    "year": datetime.now().year
                }
            )
        )

        # Push Notification
        push_response = None
        if user.fcm_token:
            push_service = (PushNotificationService())
            push_response = await (
                push_service.send_notification(
                    token=user.fcm_token,
                    title="OTP Sent for Password Reset 🔐",
                    body=(
                        "An OTP has been sent to your email for password reset. OTP: " + otp
                    )
                )
            )

        self.db.commit()
        self.db.refresh(user)

        return {
            "Status code" : status.HTTP_200_OK,
            "email": user.email,
            "message": "OTP sent successfully",
            "Email sent status" : response.get("success"),
            "push_sent": push_response.get("success") if push_response else None
        }
    

    async def verify_email_otp(self, email: str, otp: str):

        user = self.db.query(Users).filter(Users.email == email).first()

        if not user:
            return JSONResponse(
                status_code=400,
                content={
                    "message": "Invalid OTP, please try again"
                }
            )

        if not user.email_otp:
            return JSONResponse(
                status_code=400,
                content={"message": "No OTP found"}
            )

        if datetime.utcnow() > user.expires_at:

            user.email_otp = None
            user.expires_at = None

            self.db.commit()

            return JSONResponse(
                status_code=400,
                content={"message": "OTP expired Please try again"}
            )

        if user.email_otp != otp:
            self.db.commit()
            if user.fcm_token:
                push_service = PushNotificationService()
                await push_service.send_notification(
                    token=user.fcm_token,
                    title="OTP Verification Failed ❌",
                    body=(
                        "Invalid OTP entered for password reset."
                    )
                )
            return JSONResponse(
                status_code=400,
                content={"message": "Invalid OTP, please try again"}
            )

        user.email_otp = None
        user.expires_at = None

        reset_token = create_password_reset_token({"email": user.email})

        self.db.commit()
        self.db.refresh(user)

        if user.fcm_token:
            push_service = PushNotificationService()
            await push_service.send_notification(
                token=user.fcm_token,
                title="OTP Verified Successfully ✅",
                body=(
                    "OTP verified successfully for password reset."
                )
            )

        return JSONResponse(
            status_code=200,
            content={
                "message": "OTP verified successfully",
                "reset_token": reset_token,
                "email": user.email,
                "push notification_sent": True if user.fcm_token else False
            }
        )
    
    async def reset_password(self, secret_token: str, new_password: str):

        payload = decode_token(secret_token)

        if not payload:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired token"
            )

        if payload.get("type") != "password_reset":
            raise HTTPException(
                status_code=401,
                detail="Invalid token type"
            )

        email = payload.get("email")

        user = self.db.query(Users).filter(Users.email == email).first()

        if not user:
            return JSONResponse(
                status_code=400,
                content={
                    "message": "User not found, Please register first"
                }
            )

        user.password = hashpassword(new_password)
        self.db.commit()
        self.db.refresh(user)

        if user.fcm_token:
            push_service = PushNotificationService()
            await push_service.send_notification(
                token=user.fcm_token,
                title="Password Reset Successfully ✅",
                body=(
                    "Your password has been reset successfully."
                )
                )
        # Send Confirmation Email
        service = EmailService()    
        response = await service.send_email(
            EmailPayload(
                email_type="password_reset",
                to_email=email,
                subject="Your Password Changed Successfully for BlogCraft",
                payload={
                    "first_name": user.firstName, 
                    "user_email": user.email, 
                    "changed_date": datetime.now().strftime("%d %b %Y, %I:%M %p"), 
                    "login_url": "https://blog-generator-app-nu.vercel.app", 
                    "year": datetime.now().year
                }
            )
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Password reset successfully",
                "email": user.email,
                "push notification_sent": True if user.fcm_token else False,
                "Email sent status" : response.get("success")
            }
        )