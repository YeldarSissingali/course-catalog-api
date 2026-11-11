import httpx


URL = "http://127.0.0.1:8000/graphql"

read_query = '{ course(id: "api-design") { likes } }'

mutation = """
mutation {
    likeCourse(id: "api-design") {
        course {
            likes
        }
    }
}
"""

with httpx.Client(timeout=10.0) as client:
    before = client.get(URL, params={"query": read_query})
    print("BEFORE:", before.status_code, before.text)

    attempt = client.get(URL, params={"query": mutation})
    print("MUTATION:", attempt.status_code, attempt.text)

    after = client.get(URL, params={"query": read_query})
    print("AFTER:", after.status_code, after.text)