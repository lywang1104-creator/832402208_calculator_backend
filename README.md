# Student Calculator — Backend

Backend service for a split frontend/backend calculator built with **FastAPI + SQLite**. All computation happens server-side via a hand-written **Shunting-yard (postfix) parser** — `eval()` / `exec()` are **strictly forbidden**.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Web framework | FastAPI |
| ASGI server | Uvicorn |
| Database | SQLite (Python stdlib, file-based) |
| Expression parser | Hand-written Shunting-yard → postfix evaluation |

## Project Layout

```
backend/
├── src/
│   ├── __init__.py
│   ├── main.py          # FastAPI entrypoint & routes
│   ├── calculator.py    # Shunting-yard parser (core algorithm)
│   └── db.py            # SQLite data access
├── requirements.txt     # Dependencies
├── codestyle.md         # Code style guidelines
├── README.md            # This document
└── calculator.db        # Auto-generated at runtime
```

## Requirements

- Python **3.9+**

## Quick Start

```bash
# 1. Enter the backend directory
cd backend

# 2. Create a virtual environment (recommended)
python -m venv venv
# Windows activation
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the dev server
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Once running:
- API root: <http://127.0.0.1:8000/>
- Interactive docs (Swagger UI): <http://127.0.0.1:8000/docs>

## API Endpoints

### Unified Response Shape

**Success:**
```json
{"success": true, "data": {...}}
```

**Failure:**
```json
{"success": false, "message": "reason of failure"}
```

---

### 1. POST `/api/calculate` — Evaluate expression

Request body:
```json
{"expression": "(10+20)/2"}
```

Success response:
```json
{"success": true, "data": {"expression": "(10+20)/2", "result": "15"}}
```

---

### 2. GET `/api/history` — Fetch all history records

```json
{
  "success": true,
  "data": [
    {"id": 1, "expression": "1+1", "result": "2", "created_at": "2025-10-07 12:00:00"},
    {"id": 2, "expression": "(2+3)*4", "result": "20", "created_at": "2025-10-07 12:01:00"}
  ]
}
```

---

### 3. DELETE `/api/history/{record_id}` — Delete a single record

Success: `{"success": true}`

---

### 4. DELETE `/api/history` — Wipe all history (extended)

Success: `{"success": true}`

## Database

On first start the table `calculation_history` is auto-created:

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PRIMARY KEY AUTOINCREMENT | Record ID |
| expression | TEXT NOT NULL | User-supplied expression |
| result | TEXT NOT NULL | Computed result (string) |
| created_at | TIMESTAMP DEFAULT CURRENT_TIMESTAMP | Compute time |

- DB file lives at `backend/calculator.db`
- Only **successful** evaluations are persisted; failures are not stored.

## Expression Parsing Algorithm

`src/calculator.py` implements the classic **Shunting-yard** algorithm in two phases:

1. **Infix → Postfix**: an operator stack handles precedence (`* /` > `+ -`), parentheses and unary minus.
2. **Postfix evaluation**: a value stack — push numbers, pop two values per operator, push the result back.

**Supported syntax:**
- Numbers (including decimals)
- `+` `-` `*` `/`
- `(` `)`
- Negative numbers (e.g. `-3+5`, `3*(-2)`)

**Does NOT use** `eval()`, `exec()` or any third-party expression library — fully custom.

## Error Handling

| Error | Example | Returned `message` |
|-------|---------|---------------------|
| Division by zero | `10/0` | Division by zero |
| Mismatched parentheses | `(1+2` | Mismatched parentheses |
| Illegal character | `1+abc` | Illegal character |
| Syntax error | `1++2` | Expression syntax error |
| Malformed decimal | `1.2.3+4` | Malformed decimal |

## CORS

`CORSMiddleware` is configured in `main.py` with `allow_origins=["*"]`, so the frontend can call directly.

## Testing with curl

```bash
# Evaluate
curl -X POST http://127.0.0.1:8000/api/calculate \
  -H "Content-Type: application/json" \
  -d '{"expression": "(1+2)*3"}'

# Division by zero
curl -X POST http://127.0.0.1:8000/api/calculate \
  -H "Content-Type: application/json" \
  -d '{"expression": "10/0"}'

# Fetch history
curl http://127.0.0.1:8000/api/history
```

## Deployment

Recommended free platforms:
- **Render**: <https://render.com/>
- **PythonAnywhere**: <https://www.pythonanywhere.com/>

Push to GitHub and connect the repo on the platform for auto-deploy.

## License

MIT