from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class UserRole(str, Enum):
    student = "student"
    teacher = "teacher"
    admin = "admin"


class UserBase(BaseModel):
    email: str
    role: UserRole = Field(default=UserRole.student, description="Роль пользователя")

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    email: Optional[str] = None
    role: Optional[str] = None

class User(UserBase):
    id: int

    class Config:
        orm_mode = True
        from_attributes = True