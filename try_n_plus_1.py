import httpx


URL = "http://127.0.0.1:8000/graphql"

QUERIES = [
    (
        "students -> enrollments -> course",
        """
        {
            students {
                name
                enrollments {
                course {
                    title
                    }
                }
            }
        }
        """,
    ),
    (
        "enrollments -> course, student",
        """
        {
            enrollments {
                    id
                    course {
                    title
                }
                    student {
                    name
                }
            }
        }
        """,
    ),
]

with httpx.Client(timeout=30.0) as client:
    for title, query in QUERIES:
        response = client.post(
            URL,
            json={"query": query},
        )
        response.raise_for_status()

        result = response.json()

        if result.get("errors"):
            print(f"ERROR {title}: {result['errors']}")
            continue

        rows = len(
            next(iter(result["data"].values()))
        )
        queries = response.headers["x-sql-queries"]

        print(
            f"{title:<36} "
            f"rows: {rows:<3} "
            f"SQL queries: {queries}"
        )