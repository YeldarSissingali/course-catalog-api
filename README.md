# Course Catalog API

Backend на FastAPI: каталог курсов с фильтрацией, сортировкой, пагинацией, лайками и записью на курс.

## Как запустить

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1        
pip install -r requirements.txt
fastapi dev main.py
```

Документация: http://localhost:8000/docs

## What changed (Lab 5)

**CORS.** Подключён `CORSMiddleware` с `allow_origins=["http://localhost:3000"]`. Это origin
фронтенда на Next.js (схема + хост + порт, без слэша в конце). Браузер не даёт JavaScript
со страницы `localhost:3000` прочитать ответ с `localhost:8000`, пока сервер явно не
разрешит это заголовком `access-control-allow-origin`. Запросы из Server Components
идут с сервера Next.js, а не из браузера, поэтому CORS для них не нужен.

**camelCase в JSON.** Модели наследуются от `CamelModel` (`alias_generator=to_camel`,
`validate_by_name=True`, `validate_by_alias=True`). В Python поле называется `is_elective`,
в JSON `isElective`. Имена query-параметров не меняются (`?is_elective=true`).

**Новые маршруты**

| Маршрут | Ответ |
| --- | --- |
| `POST /courses/{course_id}/like` | 200, курс с увеличенным `likes`; 404, если курса нет |
| `POST /enrollments` | 201, `{"courseId": "web-security", "studentName": "Aigerim", "id": 1}`; 422 при имени короче 2 символов; 404 при неизвестном курсе |
| `GET /enrollments` | 200, список записей |

Лайки и записи хранятся в памяти и сбрасываются при каждом перезапуске сервера.
