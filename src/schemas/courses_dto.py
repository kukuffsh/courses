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
    teacher_ids: Optional[List[int]] = []

class Course(CourseBase):
    id: int
    teachers: List[int] = Field(default_factory=list)

    @classmethod
    def from_attributes(cls, obj: models.CourseRow):
        if isinstance(obj, models.CourseRow):
            data = {
                "id": obj.id,
                "name": obj.name,
                "description": obj.description,
                "banner_url": obj.banner_url,
                "schedule": obj.schedule,
                "is_from_misis": obj.is_from_misis,
                "start_date": obj.start_date,
                "end_date": obj.end_date,
                "points_per_visit": obj.points_per_visit,
                "teacher_ids": [],
                "teachers": [teacher.id for teacher in obj.teachers]
            }
            return cls(**data)
        else:
            return cls(**obj)

    class Config:
        orm_mode = True
        from_attributes = True

class User(BaseModel):
    id: int

Course.model_rebuild()