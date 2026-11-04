from sqlalchemy import text

from db import engine


with engine.connect() as conn:
    name, user = conn.execute(
        text("SELECT current_database(), current_user")
    ).one()

    version = conn.execute(
        text("SHOW server_version")
    ).scalar_one()

    counts = conn.execute(
        text(
            """
            SELECT
                (SELECT count(*) FROM courses) AS courses,
                (SELECT count(*) FROM students) AS students,
                (SELECT count(*) FROM enrollments) AS enrollments
            """
        )
    ).one()

print(f"connected to {name} as {user}, PostgreSQL {version}")
print(
    f"courses={counts.courses}, "
    f"students={counts.students}, "
    f"enrollments={counts.enrollments}"
)