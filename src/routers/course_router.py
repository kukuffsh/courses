from typing import List

from fastapi import APIRouter, status, UploadFile, File, Depends, HTTPException, Body
from sqlalchemy import Sequence

from src.service import courses_service
from src.schemas import courses_dto, user_dto, enrollment_dto, feedback_dto
import os
from src.auth.handler_auth import decodeJWT
from src.auth.bearer_auth import JWTBearer

UPLOAD_FOLDER = "courses/banners"
courses_router = APIRouter(tags=['courses'])

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@courses_router.post('/course', response_model=courses_dto.Course, status_code=status.HTTP_201_CREATED)
async def create_course(course: courses_dto.CourseCreate, jwt: JWTBearer = Depends(JWTBearer())) -> courses_dto.Course:
    """
    Creating new course. Only admin access.

    :param course:
    :param jwt:
    :return: course:
    """
    role = decodeJWT(jwt).get('role')
    return await courses_service.create_course(role, course)


@courses_router.put('/course/{course_id}', response_model=courses_dto.Course,
                    dependencies=[Depends(JWTBearer())])
async def update_banner(course_id: int, file: UploadFile = File(...),
                        jwt: JWTBearer = Depends(JWTBearer())) -> courses_dto.Course:
    """
    Update banner. Admin and teacher access.

    :param course_id:
    :param file:
    :param jwt:
    :return:
    """
    role = decodeJWT(jwt).get('role')
    return await courses_service.update_banner(role, course_id, file)


# @courses_router.put('/course/{course_id}/update_schedule', response_model=courses_dto.Course,
#                     dependencies=[Depends(JWTBearer())])
# async def update_schedule(course_id: int, schedule: courses_dto.CourseUpdate,
#                           jwt: JWTBearer = Depends(JWTBearer())) -> courses_dto.Course:
#     role = decodeJWT(jwt).get('role')
#     return await courses_service.update_schedule(role, course_id, schedule)


@courses_router.delete('/course/{course_id}/', response_model=courses_dto.Course,
                       dependencies=[Depends(JWTBearer())], status_code=status.HTTP_200_OK)
async def delete_course(course_id: int, jwt: JWTBearer = Depends(JWTBearer())) -> courses_dto.Course:
    role = decodeJWT(jwt).get('role')
    return await courses_service.delete_course(role, course_id)


@courses_router.put("/course/{course_id}", dependencies=[Depends(JWTBearer())],
                    response_model=courses_dto.Course, status_code=status.HTTP_200_OK)
async def update_course(course_id: int, filter: courses_dto.CourseUpdate,
                        jwt: JWTBearer = Depends(JWTBearer())) -> courses_dto.Course:
    role = decodeJWT(jwt).get('role')
    return await courses_service.update_course(role, course_id, filter)


@courses_router.get("/course/{course_id}/enrollments", dependencies=[Depends(JWTBearer())],
                    response_model=list[user_dto.User], status_code=status.HTTP_200_OK)
async def get_enrollments(course_id: int, jwt: JWTBearer = Depends(JWTBearer())) -> list[user_dto.User]:
    role = decodeJWT(jwt).get('role')
    return await courses_service.get_all_users_in_course(role, course_id)


@courses_router.get("/courses", response_model=List[courses_dto.Course], status_code=status.HTTP_200_OK,
                    dependencies=[Depends(JWTBearer())])
async def get_courses() -> Sequence[courses_dto.Course]:
    return await courses_service.get_all_courses()


@courses_router.post('/courses/{course_id}/teachers', response_model=courses_dto.Course,
    status_code=status.HTTP_200_OK, dependencies=[Depends(JWTBearer())])
async def add_course_teachers(course_id: int, teacher_ids: List[int],
                              jwt: JWTBearer = Depends(JWTBearer())) -> courses_dto.Course:
    """
    Adding teachers to a course. Available to course admins and teachers.

    :param course_id: Course ID
    :param teacher_ids: List of teachers ID
    :param jwt: Auth token
    :return: Updated course
    """
    user_id = decodeJWT(jwt).get('user_id')
    role = decodeJWT(jwt).get('role')
    return await courses_service.add_course_teachers(role, user_id, course_id, teacher_ids)


@courses_router.post("/enroll", response_model=enrollment_dto.Enrollment, status_code=status.HTTP_201_CREATED,
                     dependencies=[Depends(JWTBearer())])
async def enroll_on_course(course_id: int = Body(..., embed=True), jwt: JWTBearer = Depends(JWTBearer())) -> enrollment_dto.Enrollment:
    user_id = decodeJWT(jwt).get('user_id')
    
    enrollment_data = enrollment_dto.EnrollmentCreate(
        course_id=course_id,
        user_id=user_id
    )
    return await courses_service.register_user_on_course(enrollment_data)


@courses_router.post("/feedback", response_model=feedback_dto.Feedback, status_code=status.HTTP_201_CREATED,
                     dependencies=[Depends(JWTBearer())])
async def submit_feedback(filter: feedback_dto.FeedbackCreate,
                          jwt: JWTBearer = Depends(JWTBearer())) -> feedback_dto.Feedback:
    user_id = decodeJWT(jwt).get('user_id')
    filter.user_id = user_id
    return await courses_service.write_feedback(filter)
