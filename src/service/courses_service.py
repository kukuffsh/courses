from sqlalchemy import Sequence
from src.database import courses
from src.schemas import courses_dto, enrollment_dto, feedback_dto
from src.database.database import async_session
from fastapi import UploadFile, HTTPException, status
from src.database.models import models


async def create_course(course: courses_dto.CourseCreate) -> courses_dto.Course:
    async with async_session() as session:
        course = models.CourseRow(
            name=course.name,
            description=course.description,
            banner_url=course.banner_url,
            schedule=course.schedule,
            is_from_misis=course.is_from_misis,
            start_date=course.start_date,
            end_date=course.end_date,
            points_per_visit=course.points_per_visit
        )
        course = await courses.db_create_course(session, course)
        return courses_dto.Course.from_orm(course)


async def update_banner(role: str, course_id: int, file: UploadFile) -> courses_dto.Course:
    if role == 'admin':
        async with async_session() as session:
            print('hi')
            course = await courses.db_update_course_banner(session, course_id, file)
            return courses_dto.Course.from_orm(course)
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")


async def update_schedule(role: str, course_id: int, filter: courses_dto.CourseUpdate) -> courses_dto.Course:
    if role in ['admin']:
        async with async_session() as session:
            course = await courses.db_update_course_schedule(session, course_id, filter.schedule)
            return courses_dto.Course.from_orm(course)
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")


async def delete_course(role: str, course_id: int) -> courses_dto.Course:
    if role in ['admin']:
        async with async_session() as session:
            course = await courses.db_delete_course(session, course_id)
            return courses_dto.Course.from_orm(course)
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")


async def update_course(role: str, course_id: int, filter: courses_dto.CourseUpdate):
    if role in ['admin']:
        async with async_session() as session:
            course = await courses.db_update_course_info(session, course_id, filter)
            return courses_dto.Course.from_orm(course)
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")


async def get_all_users_in_course(role: str, course_id: int):
    if role in ['admin']:
        async with async_session() as session:
            return await courses.db_get_enrolled_users(session, course_id)
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")


async def get_all_courses() -> Sequence[courses_dto.Course]:
    async with async_session() as session:
        return await courses.db_get_all_courses(session)


async def register_user_on_course(filter: enrollment_dto.EnrollmentCreate) -> enrollment_dto.Enrollment:
    async with async_session() as session:
        course = await courses.db_register_user_on_course(session, filter)
        return enrollment_dto.Enrollment.from_orm(course)

async def write_feedback(filter: feedback_dto.FeedbackCreate) -> feedback_dto.Feedback:
    async with async_session() as session:
        course = await courses.db_write_feedback(session, filter)
        return feedback_dto.Feedback.from_orm(course)