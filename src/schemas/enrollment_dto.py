from pydantic import BaseModel
from typing import Optional

class EnrollmentBase(BaseModel):
    course_id: int
    user_id: int = 0
    status: str

class EnrollmentCreate(EnrollmentBase):
    pass

class Enrollment(EnrollmentBase):
    id: int

    class Config:
        orm_mode = True
        from_attributes = True