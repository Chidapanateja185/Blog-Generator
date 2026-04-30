from sqlalchemy.orm import Session
from src.models.users import Users
from src.core.security import hashpassword
from src.schemas.auth import RegisterRequest
from fastapi.responses import JSONResponse


class AuthenticationService:

    def __init__(self, db_session: Session):
        self.db = db_session

    async def register_user(self, signup_req: RegisterRequest):

        if signup_req.password != signup_req.conform_password:
            return JSONResponse(
                status_code=400,
                content={
                    "Status code": 404,
                    "message": "Passwords do not match"
                    }
            )

        existing_email = self.db.query(Users).filter(
            Users.email == signup_req.email
        ).first()

        if existing_email:
            return JSONResponse(
                status_code=400,
                content={
                    "Status code": 400,
                    "Email": signup_req.email,
                    "message": "Email already exists"
                    }
            )

        existing_mobile = self.db.query(Users).filter(
            Users.mobile == signup_req.mobile
        ).first()

        if existing_mobile:
            return JSONResponse(
                status_code=400,
                content={
                    "Status code": 400,
                    "mobile": signup_req.mobile,
                    "message": "Mobile number already exists"
                }
            )

        user = Users(
            firstName=signup_req.first_name,
            lastName=signup_req.last_name,
            email=signup_req.email,
            mobile=signup_req.mobile,
            password=hashpassword(signup_req.password),
            role="USER"
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
                "role": user.role
            }
        }