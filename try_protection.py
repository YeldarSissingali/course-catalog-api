import httpx


URL = "http://127.0.0.1:8000/graphql"

CYCLE = """
query Cycle {
  student(id: 2) {
    enrollments {
      student {
        enrollments {
          student {
            enrollments {
              id
            }
          }
        }
      }
    }
  }
}
"""

ALIASES = "{ " + " ".join(
    f'a{i}: course(id: "api-design") {{ title }}'
    for i in range(1, 13)
) + " }"

CASES = [
    ("depth 6 (cycle)", CYCLE),
    ("12 aliases", ALIASES),
    ("limit -1", "{ courses(limit: -1) { id } }"),
    ('id "abc"', '{ student(id: "abc") { name } }'),
    (
        "id of 20 digits",
        '{ student(id: "99999999999999999999") { name } }',
    ),
    (
        "introspection",
        "{ __schema { queryType { name } } }",
    ),
]

with httpx.Client(timeout=30.0) as client:
    for title, query in CASES:
        response = client.post(URL, json={"query": query})
        errors = response.json().get("errors")

        result = "data, no errors"

        if errors:
            message = errors[0]["message"].split("\n")[0]
            result = "error: " + message[:100]

        print(
            f"{title:<20} "
            f"{response.status_code}  {result}"
        )