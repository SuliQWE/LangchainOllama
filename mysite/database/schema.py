from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from .models import StatusChoices


class UserProfileInputSchema(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: EmailStr
    status: StatusChoices
    password: str


class UserProfileUpdateSchema(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: EmailStr
    status: StatusChoices


class UserProfileOutSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str
    username: str
    email: EmailStr
    status: StatusChoices
    registered_date: datetime


class UserLoginSchema(BaseModel):
    username: str
    password: str


class RequestUserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    status: StatusChoices

class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str

class FileObjectCreateSchema(BaseModel):
    dataset_file: str
    task_file: str | None = None
    image_file: str | None = None


class FileObjectResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    dataset_file: str
    task_file: str | None
    image_file: str | None
    user_id: int
    created_date: datetime
