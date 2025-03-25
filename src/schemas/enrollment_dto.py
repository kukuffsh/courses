from pydantic import BaseModel
from typing import Optional
from src.database.models import models

class EnrollmentBase(BaseModel):
    course_id: int
    user_id: int = 0
    status: str = "registered"

class EnrollmentCreate(EnrollmentBase):
    pass

class Enrollment(EnrollmentBase):
    id: int
    
    @classmethod
    def from_attributes(cls, obj: models.EnrollmentRow):
        if isinstance(obj, models.EnrollmentRow):
            data = {
                "id": obj.id,
                "course_id": obj.course_id,
                "user_id": obj.user_id,
                "status": obj.status
            }
            return cls(**data)
        else:
            return cls(**obj)

    class Config:
        orm_mode = True
        from_attributes = True