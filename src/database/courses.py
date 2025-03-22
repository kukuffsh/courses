from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from sqlalchemy.exc import SQLAlchemyError
from src.database.models import models
from src.schemas import courses_dto, enrollment_dto, feedback_dto
from sqlalchemy import select, Sequence
from typing import Optional, List
from datetime import date
from src.service import save_banner
from fastapi import UploadFile, HTTPException, status


async def db_create_course(session: AsyncSession, filter: models.CourseRow) -> models.CourseRow:
    session.add(filter)
    try:
        await session.commit()
        await session.refresh(filter)
    except IntegrityError:
        await session.rollback()
        raise ValueError("Error while adding course.")
    return filter


async def db_update_course_banner(session: AsyncSession, course_id: int, file: UploadFile) -> models.CourseRow:
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Файл должен быть изображением")

    banner_url = await save_banner.save_banner_to_storage(file, course_id)

    query = select(models.CourseRow).where(models.CourseRow.id == course_id)
    result = await session.execute(query)
    course = result.scalar_one_or_none()

    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Курс не найден")
    course.banner_url = banner_url
    await session.commit()

    return course


async def db_update_course_schedule(session: AsyncSession, course_id: int, schedule) -> models.CourseRow:
    query = select(models.CourseRow).where(models.CourseRow.id == course_id)
    result = await session.execute(query)
    course = result.scalar_one_or_none()
    if not course:
        raise ValueError("Course not found.")

    course.schedule = schedule
    await session.commit()
    await session.refresh(course)
    return course


async def db_update_course_dates(session: AsyncSession, course_id: int, start_date: Optional[date] = None,
                                 end_date: Optional[date] = None) -> models.CourseRow:
    query = select(models.CourseRow).where(models.CourseRow.id == course_id)
    result = await session.execute(query)
    course = result.scalar_one_or_none()
    if not course:
        raise ValueError("Course not found.")

    if start_date:
        course.start_date = start_date
    if end_date:
        course.end_date = end_date

    await session.commit()
    await session.refresh(course)
    return course


async def db_update_course_info(session: AsyncSession, course_id: int,
                                filter: courses_dto.CourseUpdate) -> models.CourseRow:
    query = select(models.CourseRow).where(models.CourseRow.id == course_id)
    result = await session.execute(query)
    course = result.scalar_one_or_none()

    if not course:
        raise ValueError("Course not found.")

    if filter.name is not None:
        course.name = filter.name
    if filter.description is not None:
        course.description = filter.description
    if filter.is_from_misis is not None:
        course.is_from_misis = filter.is_from_misis
    if filter.start_date is not None:
        course.start_date = filter.start_date
    if filter.end_date is not None:
        course.end_date = filter.end_date
    if filter.points_per_visit is not None:
        course.points_per_visit = filter.points_per_visit

    try:
        await session.commit()
        await session.refresh(course)
    except Exception:
        await session.rollback()
        raise

    return course


async def db_delete_course(session: AsyncSession, course_id: int) -> models.CourseRow:
    try:
        query = select(models.CourseRow).where(models.CourseRow.id == course_id)
        result = await session.execute(query)
        course = result.scalar_one_or_none()

        if course is None:
            raise Exception(f"Course with ID {course_id} not found")

        await session.delete(course)
        await session.commit()

        return course

    except SQLAlchemyError as e:
        await session.rollback()  # Откатываем транзакцию в случае ошибки
        raise Exception(f"Error deleting course with ID {course_id}: {str(e)}")


async def db_get_enrolled_users(session: AsyncSession, course_id: int) -> Sequence[models.UserRow]:
    query = select(models.UserRow).join(models.EnrollmentRow).where(models.EnrollmentRow.course_id == course_id)
    result = await session.execute(query)
    users = result.scalars().all()

    return users


async def db_get_all_courses(session) -> Sequence[models.UserRow]:
    result = await session.execute(
        select(models.CourseRow)
        .options(selectinload(models.CourseRow.teachers))
    )
    return result.scalar_one_or_none()


async def db_register_user_on_course(session: AsyncSession,
                                     enrollment_data: enrollment_dto.EnrollmentCreate) -> models.EnrollmentRow:
    query_course = select(models.CourseRow).where(models.CourseRow.id == enrollment_data.course_id)
    result_course = await session.execute(query_course)
    course = result_course.scalar_one_or_none()

    if not course:
        raise ValueError("Course not found")

    query_user = select(models.UserRow).where(models.UserRow.id == enrollment_data.user_id)
    result_user = await session.execute(query_user)
    user = result_user.scalar_one_or_none()

    if not user:
        raise ValueError("User not found")

    query_existing_enrollment = select(models.EnrollmentRow).where(
        models.EnrollmentRow.user_id == enrollment_data.user_id,
        models.EnrollmentRow.course_id == enrollment_data.course_id
    )
    result_enrollment = await session.execute(query_existing_enrollment)
    existing_enrollment = result_enrollment.scalar_one_or_none()

    if existing_enrollment:
        raise ValueError("User already registered for this course")

    new_enrollment = models.EnrollmentRow(
        user_id=enrollment_data.user_id,
        course_id=enrollment_data.course_id,
        status="registered"
    )

    session.add(new_enrollment)
    await session.commit()

    return new_enrollment


async def db_write_feedback(session: AsyncSession, filter: feedback_dto.FeedbackCreate) -> models.FeedbackRow:
    query_course = select(models.CourseRow).where(models.CourseRow.id == filter.course_id)
    result_course = await session.execute(query_course)
    course = result_course.scalar_one_or_none()

    if not course:
        raise ValueError("Course not found")

    new_feedback = models.FeedbackRow(
        user_id=filter.user_id,
        course_id=filter.course_id,
        rating=filter.rating,
        comment=filter.comment
    )

    session.add(new_feedback)
    await session.commit()
    await session.refresh(new_feedback)

    return new_feedback


async def get_course_by_id(session: AsyncSession, course_id: int,
                           load_teachers: bool = False) -> Optional[models.CourseRow]:
    try:
        query = select(models.CourseRow).where(models.CourseRow.id == course_id)

        if load_teachers:
            query = query.options(selectinload(models.CourseRow.teachers))

        result = await session.execute(query)
        return result.scalar_one_or_none()

    except Exception as e:
        raise ValueError(f"Database error: {str(e)}") from e

async def get_full_course(session: AsyncSession, course_id: int) -> models.CourseRow:
    result = await session.execute(
        select(models.CourseRow)
        .options(selectinload(models.CourseRow.teachers))
        .where(models.CourseRow.id == course_id)
    )
    return result.scalar_one_or_none()


async def db_add_course_teachers(
        session: AsyncSession,
        course_id: int,
        teacher_ids: List[int]
) -> None:
    try:
        existing_links = await session.execute(
            select(models.course_teachers).where(
                models.course_teachers.course_id == course_id,
                models.course_teachers.teacher_id.in_(teacher_ids)
            )
        )
        existing_ids = {link.teacher_id for link in existing_links.scalars()}
        new_ids = [id for id in teacher_ids if id not in existing_ids]

        if new_ids:
            session.add_all([
                models.course_teachers(
                    course_id=course_id,
                    teacher_id=teacher_id
                ) for teacher_id in new_ids
            ])
            await session.commit()

    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(
            status_code=400,
            detail="Ошибка при добавлении преподавателей"
        ) from e