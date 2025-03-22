from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import Optional, Dict, Any, List
from datetime import date
from src.database.models import models

class CourseBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    banner_url: Optional[str] = None
    schedule: Optional[Dict[str, Any]] = None
    is_from_misis: bool
    start_date: date
    end_date: date
    points_per_visit: float = Field(..., gt=0)
    teacher_ids: List[int] = Field(default_factory=list)

    @model_validator(mode='after')
    def check_dates(self):
        if self.start_date >= self.end_date:
            raise ValueError('end_date must be greater than start_date')
        return self

class CourseCreate(CourseBase):
    pass

class CourseUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    banner_url: Optional[str] = None
    schedule: Optional[Dict[str, Any]] = None
    is_from_misis: Optional[bool] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    points_per_visit: Optional[float] = Field(None, gt=0)
    teacher_ids: Optional[List[int]] = None

class Course(CourseBase):
    id: int
    teachers: List['User'] = Field(default_factory=list)

    @classmethod
    def from_attributes(cls, obj: dict):
        if isinstance(obj, models.CourseRow):
            obj = obj.__dict__
        return cls(**obj)

    class Config:
        orm_mode = True

class User(BaseModel):
    id: int
    name: str

Course.model_rebuild()