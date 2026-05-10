from urllib import response

from jose import JWTError, jwt
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from fastapi import status
from datetime import datetime, timedelta

from src.models.users import Users
from src.schemas.auth import LoginRequest, LoginResponse, RegisterRequest
from src.services.email_service import EmailPayload, EmailService
from src.core.security import (
    hashpassword,
    verify_password,
    create_access_token,
    create_refresh_token,
    SECRET_KEY,
    ALGORITHM
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
            role="USER"
        )

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