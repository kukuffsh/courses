from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import date


class CourseBase(BaseModel):
    name: str
    description: Optional[str] = None
    banner_url: Optional[str] = None
    schedule: Optional[Dict[str, Any]] = None
    is_from_misis: bool
    start_date: date
    end_date: date
    points_per_visit: float


class CourseCreate(CourseBase):
    pass


class CourseUpdate(CourseBase):
    name: Optional[str] = None
    description: Optional[str] = None
    banner_url: Optional[str] = None
    schedule: Optional[Dict[str, Any]] = None
    is_from_misis: Optional[bool] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    points_per_visit: Optional[float] = None


class Course(CourseBase):
    id: int

    class Config:
        orm_mode = True
        from_attributes = True
