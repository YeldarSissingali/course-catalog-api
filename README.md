# course-catalog-api

Course catalog API built with FastAPI, SQLAlchemy, PostgreSQL, Alembic and Strawberry GraphQL. REST and GraphQL share the same database and application services.

## How to run

Requirements: Python 3.11 or newer and PostgreSQL 16 or newer.

The local PostgreSQL server used for this project listens on port **5433**. Adjust the commands and database URL if your port differs.

Once, connect as the PostgreSQL administrator:

```powershell
& "C:\Program Files\PostgreSQL\16\bin\psql.exe" -h localhost -p 5433 -U postgres -d postgres
```

Create the role and database if they do not exist:

```sql
CREATE ROLE catalog_app LOGIN PASSWORD 'change-me';
CREATE DATABASE course_catalog OWNER catalog_app;
```

Exit with `\q`.

From the backend project folder:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` with your local credentials:

```dotenv
DATABASE_URL=postgresql+psycopg://catalog_app:change-me@localhost:5433/course_catalog
SQL_ECHO=false
GRAPHQL_INTROSPECTION=true
```

`change-me` is a training example. Use the actual password of your local role. The `.env` file is excluded from Git.

Create the tables and load initial data:

```powershell
.\.venv\Scripts\alembic.exe upgrade head
& "C:\Program Files\PostgreSQL\16\bin\psql.exe" -h localhost -p 5433 -U catalog_app -d course_catalog -v ON_ERROR_STOP=1 -f seed.sql
.\.venv\Scripts\alembic.exe check
```

`seed.sql` clears the catalog tables and restores 6 courses, 3 students and 6 enrollments. It is intended for the training database.

Start the API:

```powershell
.\.venv\Scripts\fastapi.exe dev main.py
```

- REST documentation: http://127.0.0.1:8000/docs
- GraphiQL: http://127.0.0.1:8000/graphql

In another terminal, from the backend folder:

```powershell
.\.venv\Scripts\python.exe try_errors.py
.\.venv\Scripts\python.exe try_graphql.py
.\.venv\Scripts\python.exe try_n_plus_1.py
.\.venv\Scripts\python.exe try_protection.py
.\.venv\Scripts\python.exe flood_likes.py
.\.venv\Scripts\python.exe measure.py
```

Expected results: 5 REST checks passed, 8 GraphQL checks passed, and both nested queries use 3 SQL queries. The protected flood request is rejected with 0 SQL queries.

For the frontend, from its own project folder:

```powershell
npm install
npm run dev
```

Its `.env.local` must contain:

```dotenv
API_URL=http://127.0.0.1:8000
```

Open http://localhost:3000/my-courses and http://localhost:3000/my-courses-rest. Both pages show student 2 and the same three courses.

A clean-start check was completed: the training database was recreated, both Alembic migrations were applied, seed data was loaded and the checks passed.

## What changed in the API

- Application rules moved to `services.py`. REST and GraphQL call the same functions for creating students, enrolling and liking courses.
- Expected service errors have stable codes such as `ALREADY_ENROLLED`.
- REST translates service errors through `problem.py` into Problem Details with content type `application/problem+json`.
- Pydantic validation errors still use FastAPI's standard 422 JSON format in the core solution.
- `/graphql` accepts GraphQL queries and mutations. Opening it in a browser displays GraphiQL, a development query editor.
- Queries expose courses, students, enrollments and their relationships.
- Mutations expose `enroll` and `likeCourse`. Expected rule errors appear in the payload's `userErrors`; query and unexpected execution errors appear in top-level `errors`.
- `X-SQL-Queries` reports SQL statements executed during each HTTP request.
- Request-scoped DataLoaders batch relationship loading.
- Protection limits query depth to 5, aliases to 10 and list limits to 1–100. Invalid numeric IDs receive a clear error; unexpected exceptions are masked.
- `GRAPHQL_INTROSPECTION` controls schema introspection.
- New REST routes provide `GET /students/{id}` and `GET /students/{id}/enrollments`.
- The frontend implements the same “My courses” screen through REST and GraphQL using server components and `cache: "no-store"`.

## Example queries

Run the following in GraphiQL.

### My courses

```graphql
query MyCourses($id: ID!) {
  student(id: $id) {
    name
    enrollments {
      id
      course {
        title
        credits
        level
      }
    }
  }
}
```

Variables:

```json
{
  "id": "2"
}
```

The response contains Bogedaev Yerbolat and three courses: Modern Frontend, Backend Foundations and AI/LLM Integration.

### Enroll

```graphql
mutation Enroll($input: EnrollInput!) {
  enroll(input: $input) {
    enrollment {
      id
      enrolledAt
      course {
        title
      }
    }
    userErrors {
      code
      message
    }
  }
}
```

Variables for a new enrollment on the starting data:

```json
{
  "input": {
    "courseId": "web-security",
    "studentId": "3"
  }
}
```

A successful response contains an enrollment object with a database-generated ID and timestamp, and an empty `userErrors` list.

Repeating the mutation returns:

```json
{
  "data": {
    "enroll": {
      "enrollment": null,
      "userErrors": [
        {
          "code": "ALREADY_ENROLLED",
          "message": "Student is already enrolled in this course"
        }
      ]
    }
  }
}
```

### Like a course

```graphql
mutation {
  likeCourse(id: "api-design") {
    course {
      id
      likes
    }
    userErrors {
      code
      message
    }
  }
}
```

Mutations change training data. Run `seed.sql` before repeating measurements.

## REST vs GraphQL comparison

The measured screen shows student 2 and their three courses on the starting dataset. Byte counts are response-body sizes reported by `measure.py`.

| Criterion | REST | GraphQL | Source |
|---|---|---|---|
| Requests and rounds per screen | 5 requests, 2 rounds | 1 request, 1 round | `measure.py` |
| Response bytes | 1162 | 343 | `measure.py` |
| SQL queries per screen | 5 | 3 | `X-SQL-Queries`, `measure.py` |
| SQL growth with more students | These REST routes have explicit queries; this lab did not measure a REST student-list growth scenario. | Before DataLoaders: 7/7 queries on starting data, 27/24 with more students. With DataLoaders: 3/3 on both datasets. | `try_n_plus_1.py` |
| Query or request error | Status identifies errors, such as 404 or 422. | Tested query errors return HTTP 200 with `errors`; clients must inspect JSON. | Experiments 1 and 8 |
| Repeated enrollment | 409, Problem Details | HTTP 200, `userErrors` with `ALREADY_ENROLLED` | REST and GraphQL checks |
| HTTP cache | GET resource URLs work naturally with HTTP caching when configured. | The POST requests used here require additional caching design. GraphQL queries can also use GET. Both lab pages disable fetch caching. | Design comparison; not measured |
| Expensive-query protection | Routes control their query shape; this project has no per-client rate limiter. | Depth, alias and argument limits; unexpected-error masking; optional introspection disabling. These do not replace authorization or rate limiting. | Experiments 6 and 7 |

For a simple course lookup I would keep REST because one route already provides the needed resource. For “My courses”, GraphQL reduces the implemented screen from five requests in two rounds to one request in one round. DataLoaders reduce its SQL work from five calls in the REST implementation to three. A dedicated REST aggregation route could also reduce requests; these measurements compare the implementations in this lab.

## Experiment log

| # | Experiment | What I saw | Cause | How I fixed it |
|---|---|---|---|---|
| 1 | Requested `titel` and used argument `is_elective`. | HTTP 200 with `errors` and `data: null`. | The query did not match the GraphQL schema; public names use camelCase. | Restored `title` and `isElective`. |
| 2 | Removed `None` from the course result type. | A missing course caused a non-null error; in a query with aliases the entire data became null. | The resolver broke the schema's non-null promise. | Restored `CourseType \| None`; the existing result remained available alongside a null missing course. |
| 3 | Sent a mutation using GET. | HTTP 400; likes did not change. | GET mutations are rejected because GET is intended for safe reading. | Used POST for mutations. |
| 4 | Added 17 students with `more_students.sql`. | Nested query counts grew from 7/7 to 27/24. | Lazy relationship loading caused separate database calls per object. | Added request-scoped DataLoaders in the next step. |
| 5 | Returned raw rows from the batch function in reverse order. | One query failed with the wrong result count; another returned incorrect course associations without an error. | DataLoader matches results to keys by position, so both length and order matter. | Grouped rows by key and returned one result per input key in key order. |
| 6 | Sent deep queries, 12 aliases, invalid limits and IDs, and a schema query before and after protection. | Unprotected requests exposed errors or performed 12 likes. Protection rejected excessive depth/aliases, validated arguments and masked internal exceptions. The protected flood made 0 SQL queries. | Clients control GraphQL query shape and can request excessive work. | Installed depth and alias limits, argument checks and MaskErrors. |
| 7 | Disabled introspection and sent a query with a typo. | Schema introspection failed, but normal queries worked and error suggestions still named fields. | Disabling introspection does not hide all schema information or enforce permissions. | Restored intros