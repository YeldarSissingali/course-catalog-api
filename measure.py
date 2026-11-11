import asyncio

import httpx


API = "http://127.0.0.1:8000"
STUDENT = 2

MY_COURSES = """
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
"""


async def rest(client: httpx.AsyncClient):

    first = await asyncio.gather(
        client.get(f"/students/{STUDENT}"),
        client.get(f"/students/{STUDENT}/enrollments"),
    )

    for response in first:
        response.raise_for_status()


    codes = [
        item["courseId"]
        for item in first[1].json()
    ]

    second = await asyncio.gather(
        *(
            client.get(f"/courses/{code}")
            for code in codes
        )
    )

    for response in second:
        response.raise_for_status()

    return [*first, *second], 2


async def graphql(client: httpx.AsyncClient):
    response = await client.post(
        "/graphql",
        json={
            "query": MY_COURSES,
            "variables": {"id": str(STUDENT)},
        },
    )
    response.raise_for_status()

    body = response.json()

    if body.get("errors"):
        raise RuntimeError(body["errors"])

    if body["data"]["student"] is None:
        raise RuntimeError("Student not found")

    return [response], 1


async def main():
    print(
        f"{'':<8} "
        f"{'requests':<9} "
        f"{'rounds':<7} "
        f"{'bytes':<7} "
        "SQL queries"
    )

    async with httpx.AsyncClient(
        base_url=API,
        timeout=30.0,
    ) as client:
        for name, run in (
            ("REST", rest),
            ("GraphQL", graphql),
        ):
            responses, rounds = await run(client)

            size = sum(
                len(response.content)
                for response in responses
            )

            sql = sum(
                int(response.headers["x-sql-queries"])
                for response in responses
            )

            print(
                f"{name:<8} "
                f"{len(responses):<9} "
                f"{rounds:<7} "
                f"{size:<7} "
                f"{sql}"
            )


asyncio.run(main())