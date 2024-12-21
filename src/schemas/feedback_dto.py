from pydantic import BaseModel, Field
from typing import Optional

class FeedbackBase(BaseModel):
    course_id: int
    rating: int = Field(..., ge=1, le=5, description="Оценка курса от 1 до 5")
    comment: Optional[str] = None

class FeedbackCreate(FeedbackBase):
    user_id: int = 0

class Feedback(FeedbackBase):
    id: int

    class Config:
        orm_mode = True
        from_attributes = True