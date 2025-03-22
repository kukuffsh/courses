from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey, Text, Float, JSON, DateTime, Table
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

#Доп. Таблица ассоциаций
course_teachers = Table(
    'course_teachers', Base.metadata,
    Column('course_id', Integer, ForeignKey('course.id'), primary_key=True),
    Column('teacher_id', Integer, ForeignKey('user.id'), primary_key=True),
    Column('is_main', Boolean, default=False)
)

class CourseRow(Base):
    __tablename__ = 'course'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    banner_url = Column(String, nullable=True)
    schedule = Column(JSON, nullable=True)
    is_from_misis = Column(Boolean, default=False, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    points_per_visit = Column(Float, nullable=False)

    teachers = relationship(
        'UserRow',
        secondary=course_teachers,
        back_populates='courses'
    )
    feedback = relationship("FeedbackRow", back_populates="course")
    enrollments = relationship("EnrollmentRow", back_populates="course")

class UserRow(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False)
    role = Column(String, nullable=False)

    enrollments = relationship("EnrollmentRow", back_populates="user")
    feedback = relationship("FeedbackRow", back_populates="user")
    logs = relationship("LogRow", back_populates="user")
    courses = relationship(
        'CourseRow',
        secondary=course_teachers,
        back_populates='teachers'
    )


class EnrollmentRow(Base):
    __tablename__ = 'enrollment'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    course_id = Column(Integer, ForeignKey('course.id'), nullable=False)
    status = Column(String, nullable=False)

    user = relationship("UserRow", back_populates="enrollments")
    course = relationship("CourseRow", back_populates="enrollments")
    attendance = relationship("AttendanceRow", back_populates="enrollment")

class AttendanceRow(Base):
    __tablename__ = 'attendance'

    id = Column(Integer, primary_key=True, autoincrement=True)
    enrollment_id = Column(Integer, ForeignKey('enrollment.id'), nullable=False)
    lesson_date = Column(Date, nullable=False)
    is_attended = Column(Boolean, nullable=False)

    enrollment = relationship("EnrollmentRow", back_populates="attendance")

class FeedbackRow(Base):
    __tablename__ = 'feedback'

    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey('course.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    rating = Column(Float, nullable=False)
    comment = Column(Text, nullable=True)

    course = relationship("CourseRow", back_populates="feedback")
    user = relationship("UserRow", back_populates="feedback")

class LogRow(Base):
    __tablename__ = 'logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    action = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)

    user = relationship("UserRow", back_populates="logs")