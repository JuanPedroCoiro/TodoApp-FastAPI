from datetime import timedelta, datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, Request, HTTPException, Response
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
from jose import jwt, JWTError
from pydantic import BaseModel

from database import SessionLocal
from models import Users

router = APIRouter(prefix="/auth", tags=["auth"])

SECRET_KEY = '588d349958d99a234962dc3929ed65a265835324d44af0f623bd39ce417af5c6'
ALGORITHM = 'HS256'
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated='auto')
templates = Jinja2Templates(directory="TodoApp/templates")


# --- DB dependency ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


# --- Schemas ---
class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str
    phone_number: str


# --- Pages ---
@router.get("/login-page")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/register-page")
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


# --- Helpers ---
def authenticate_user(username: str, password: str, db: Session):
    user = db.query(Users).filter(Users.username == username).first()
    if not user or not bcrypt_context.verify(password, user.hashed_password):
        return None
    return user


def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta):
    payload = {
        "sub": username,
        "id": user_id,
        "role": role,
        "exp": datetime.now(timezone.utc) + expires_delta
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("id")
        if not user_id:
            return None
        return {"user_id": user_id}
    except JWTError:
        return None


# --- Endpoints ---
@router.post("/")
async def create_user(user: CreateUserRequest, db: db_dependency):
    db_user = Users(
        username=user.username,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,
        phone_number=user.phone_number,
        hashed_password=bcrypt_context.hash(user.password),
        is_active=True
    )
    db.add(db_user)
    db.commit()
    return {"message": "User created"}


@router.post("/token")
async def login_for_access_token(
        response: Response,
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: db_dependency
):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=401, detail="Could not validate credentials.")

    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=20))

    response = RedirectResponse(url="/todos/todo-page", status_code=302)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False
    )
    return response
