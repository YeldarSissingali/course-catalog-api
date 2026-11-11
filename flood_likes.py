import httpx


URL = "http://127.0.0.1:8000/graphql"

operations = " ".join(
    f'a{i}: likeCourse(id: "api-design") '
    "{ course { likes } }"
    for i in range(1, 13)
)

response = httpx.post(
    URL,
    json={"query": "mutation { " + operations + " }"},
    timeout=30.0,
)

body = response.json()

print("HTTP status:", response.status_code)

if body.get("errors"):
    print("error:", body["errors"][0]["message"])
else:
    print(
        "likes:",
        [
            body["data"][f"a{i}"]["course"]["likes"]
            for i in range(1, 13)
        ],
    )

print(
    "SQL queries:",
    response.headers["x-sql-queries"],
)