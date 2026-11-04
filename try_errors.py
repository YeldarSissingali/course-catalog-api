import httpx


BASE = "http://127.0.0.1:8000"

CASES = [
    (
        "email already taken",
        "/students",
        {
            "name": "Yeldar Two",
            "email": "Yeldar@example.com",
        },
        409,
    ),
    (
        "already enrolled",
        "/enrollments",
        {
            "courseId": "ai-integration",
            "studentId": 3,
        },
        409,
    ),
    (
        "unknown course",
        "/enrollments",
        {
            "courseId": "nope",
            "studentId": 3,
        },
        404,
    ),
    (
        "unknown student",
        "/enrollments",
        {
            "courseId": "web-security",
            "studentId": 999,
        },
        404,
    ),
    (
        "name too short",
        "/students",
        {
            "name": "N",
            "email": "n@example.com",
        },
        422,
    ),
]

failed = 0

with httpx.Client(base_url=BASE, timeout=10.0) as client:
    for title, path, body, expected in CASES:
        response = client.post(path, json=body)
        ok = response.status_code == expected

        if not ok:
            failed += 1

        mark = "ok" if ok else "FAIL"

        print(
            f"{mark:4} {title:<22} "
            f"{response.status_code}  {response.text}"
        )

print(f"{len(CASES) - failed} of {len(CASES)} as expected")