from sqlalchemy import select
from sqlalchemy.orm import Session

from db import engine
from models import Course, Enrollment, Student


with Session(engine) as session:
    courses = session.scalars(
        select(Course).order_by(Course.id)
    ).all()

    students = session.scalars(
        select(Student).order_by(Student.id)
    ).all()

    enrollments = session.scalars(
        select(Enrollment).order_by(Enrollment.id)
    ).all()

    print(
        f"courses={len(courses)}, "
        f"students={len(students)}, "
        f"enrollments={len(enrollments)}"
    )

    if enrollments:
        enrollment = enrollments[0]
        print(
            f"Enrollment #{enrollment.id}: "
            f"{enrollment.student.name} -> "
            f"{enrollment.course.title}"
        )
        print(f"Enrolled at: {enrollment.enrolled_at}")