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
        

from sqlalchemy import inspect

from db import Base


inspector = inspect(engine)

model_names = set()
database_names = set()

for table_name, table in Base.metadata.tables.items():
    for constraint in table.constraints:
        if constraint.name is not None:
            model_names.add(str(constraint.name))

    primary_key = inspector.get_pk_constraint(table_name)
    if primary_key["name"]:
        database_names.add(primary_key["name"])

    for constraint in inspector.get_unique_constraints(table_name):
        if constraint["name"]:
            database_names.add(constraint["name"])

    for constraint in inspector.get_check_constraints(table_name):
        if constraint["name"]:
            database_names.add(constraint["name"])

    for constraint in inspector.get_foreign_keys(table_name):
        if constraint["name"]:
            database_names.add(constraint["name"])

print(
    "names only in models:",
    sorted(model_names - database_names) or "none",
)
print(
    "names only in database:",
    sorted(database_names - model_names) or "none",
)        