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
        "email-taken",
    ),
    (
        "already enrolled",
        "/enrollments",
        {
            "courseId": "ai-integration",
            "studentId": 3,
        },
        409,
        "already-enrolled",
    ),
    (
        "unknown course",
        "/enrollments",
        {
            "courseId": "nope",
            "studentId": 3,
        },
        404,
        "course-not-found",
    ),
    (
        "unknown student",
        "/enrollments",
        {
            "courseId": "web-security",
            "studentId": 999,
        },
        404,
        "student-not-found",
    ),
    (
        "name too short",
        "/students",
        {
            "name": "N",
            "email": "n@example.com",
        },
        422,
        None,
    ),
]

failed = 0

with httpx.Client(base_url=BASE, timeout=10.0) as client:
    for title, path, body, status, slug in CASES:
        response = client.post(path, json=body)

        kind = (
            response.json()
            .get("type", "-")
            .rsplit("/", 1)[-1]
        )

        content_type = response.headers.get(
            "content-type", ""
        ).split(";")[0]

        expected_content_type = (
            "application/problem+json"
            if slug is not None
            else "application/json"
        )

        ok = (
            response.status_code == status
            and (slug is None or kind == slug)
            and content_type == expected_content_type
        )

        if not ok:
            failed += 1

        mark = "ok" if ok else "FAIL"

        print(
            f"{mark:4} {title:<22} "
            f"{response.status_code}  "
            f"{content_type:<25} {kind}"
        )

print(f"{len(CASES) - failed} of {len(CASES)} as expected")