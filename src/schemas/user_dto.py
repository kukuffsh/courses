from pydantic import BaseModel
from typing import Optional

class UserBase(BaseModel):
    email: str
    role: str

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