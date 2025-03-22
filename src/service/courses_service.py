from sqlalchemy import Sequence
from src.database import courses, users
from typing import List
from src.schemas import courses_dto, enrollment_dto, feedback_dto
from src.database.database import async_session
from fastapi import UploadFile, HTTPException
from src.database.models import models
from functools import wraps


def admin_access(func):
    @wraps(func)
    async def wrapper(role: str, *args, **kwargs):
        if role != "admin":
            raise HTTPException(403, "Forbidden")
        return await func(role, *args, **kwargs)

    return wrapper

def teacher_admin_access(func):
    @wraps(func)
    async def wrapper(role: str, *args, **kwargs):
        if role != "admin" and role != "teacher":
            raise HTTPException(403, "Forbidden")
        return await func(role, *args, **kwargs)

    return wrapper

@admin_access
async def create_course(role, course: courses_dto.CourseCreate) -> courses_dto.Course:
    async with async_session() as session:
        teachers = await users.get_users_by_ids(session, course.teacher_ids)
        course = models.CourseRow(
            name=course.name,
            description=course.description,
            banner_url=course.banner_url,
            schedule=course.schedule,
            is_from_misis=course.is_from_misis,
            start_date=course.start_date,
            end_date=course.end_date,
            points_per_visit=course.points_per_visit,
        )
        course.teachers.extend(teachers)
        course = await courses.db_create_course(session, course)
        return courses_dto.Course.from_attributes(course)


@teacher_admin_access
async def update_banner(role: str, course_id: int, file: UploadFile) -> courses_dto.Course:
    async with async_session() as session:
        course = await courses.db_update_course_banner(session, course_id, file)
        return courses_dto.Course.from_attributes(course)


@teacher_admin_access
async def update_schedule(role: str, course_id: int, filter: courses_dto.CourseUpdate) -> courses_dto.Course:
    async with async_session() as session:
        course = await courses.db_update_course_schedule(session, course_id, filter.schedule)
        return courses_dto.Course.from_attributes(course)


@admin_access
async def delete_course(role: str, course_id: int) -> courses_dto.Course:
    async with async_session() as session:
        course = await courses.db_delete_course(session, course_id)
        return courses_dto.Course.from_attributes(course)


@teacher_admin_access
async def update_course(role: str, course_id: int, filter: courses_dto.CourseUpdate):
    async with async_session() as session:
        course = await courses.db_update_course_info(session, course_id, filter)
        return courses_dto.Course.from_attributes(course)


@teacher_admin_access
async def get_all_users_in_course(role: str, course_id: int):
    async with async_session() as session:
        return await courses.db_get_enrolled_users(session, course_id)


async def add_course_teachers(
        role: str,
        current_user_id: int,
        course_id: int,
        teacher_ids: List[int]
) -> courses_dto.Course:
    async with async_session() as session:
        course = await courses.get_course_by_id(session, course_id)
        if not course:
            raise HTTPException(status_code=404, detail="Курс не найден")

        existing_teachers = await users.get_users_by_ids(session, teacher_ids)
        if len(existing_teachers) != len(teacher_ids):
            raise HTTPException(status_code=404, detail="Один или несколько преподавателей не найдены")

        await courses.db_add_course_teachers(session, course_id, teacher_ids)

        updated_course = await courses.get_full_course(session, course_id)
        return courses_dto.Course.from_orm(updated_course)


async def get_all_courses() -> Sequence[courses_dto.Course]:
    async with async_session() as session:
        return await courses.db_get_all_courses(session)


async def register_user_on_course(filter: enrollment_dto.EnrollmentCreate) -> enrollment_dto.Enrollment:
    async with async_session() as session:
        course = await courses.db_register_user_on_course(session, filter)
        return enrollment_dto.Enrollment.from_attributes(course)


async def write_feedback(filter: feedback_dto.FeedbackCreate) -> feedback_dto.Feedback:
    async with async_session() as session:
        course = await courses.db_write_feedback(session, filter)
        return feedback_dto.Feedback.from_attributes(course)
