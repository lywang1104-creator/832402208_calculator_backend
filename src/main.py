"""
main.py - FastAPI entry point
Provides 4 RESTful API endpoints:
  POST   /api/calculate            - Evaluate expression & save history
  GET    /api/history              - Retrieve all history records
  DELETE /api/history/{record_id}  - Delete a single history record
  DELETE /api/history              - Clear all history (optional extension)
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager

from src.calculator import calculate, format_result, ExpressionError, DivideByZeroError
from src.db import init_db, save_history, get_all_history, delete_history_by_id, clear_all_history


# ---------------------------------------------------------------------------
# Lifespan: auto-init DB tables at startup
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


# ---------------------------------------------------------------------------
# FastAPI app + CORS middleware
# ---------------------------------------------------------------------------
app = FastAPI(title="Student Calculator API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # Allow all origins (simplified for assignment)
    allow_credentials=True,
    allow_methods=["*"],       # Allow all HTTP methods
    allow_headers=["*"],       # Allow all request headers
)


# ---------------------------------------------------------------------------
# Pydantic request model
# ---------------------------------------------------------------------------
class CalculateRequest(BaseModel):
    expression: str = Field(..., description="Math expression string", min_length=1, max_length=500)


# ---------------------------------------------------------------------------
# Generic response helpers
# ---------------------------------------------------------------------------
def ok_response(data=None):
    return {"success": True, "data": data}


def fail_response(message: str):
    return {"success": False, "message": message}


# ---------------------------------------------------------------------------
# Global exception handler
# ---------------------------------------------------------------------------
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return fail_response(f"Internal server error: {str(exc)}")


# -------------------------------------------------------
# Endpoint 1: POST /api/calculate - Core calculation
# -------------------------------------------------------
@app.post("/api/calculate")
async def api_calculate(req: CalculateRequest):
    try:
        raw_expr = req.expression.strip()
        if not raw_expr:
            return fail_response("Expression must not be empty")

        # Perform calculation
        value = calculate(raw_expr)
        result_str = format_result(value)

        # Persist only successful records
        save_history(raw_expr, result_str)

        return ok_response({
            "expression": raw_expr,
            "result": result_str,
        })

    except DivideByZeroError as e:
        return fail_response(str(e))

    except ExpressionError as e:
        return fail_response(str(e))

    except Exception as e:
        return fail_response(f"Calculation failed: {str(e)}")


# -------------------------------------------------------
# Endpoint 2: GET /api/history - List all records
# -------------------------------------------------------
@app.get("/api/history")
async def api_get_history():
    records = get_all_history()
    return ok_response(records)


# -------------------------------------------------------
# Endpoint 4 (optional): DELETE /api/history - Clear all
# NOTE: must be registered BEFORE /api/history/{record_id}
#       otherwise it will be matched as a parameter.
# -------------------------------------------------------
@app.delete("/api/history")
async def api_clear_history():
    clear_all_history()
    return ok_response()


# -------------------------------------------------------
# Endpoint 3: DELETE /api/history/{record_id} - Delete one
# -------------------------------------------------------
@app.delete("/api/history/{record_id}")
async def api_delete_history_one(record_id: int):
    if record_id <= 0:
        return fail_response("Invalid record ID")
    deleted = delete_history_by_id(record_id)
    if not deleted:
        return fail_response(f"Record {record_id} does not exist")
    return ok_response()

# -------------------------------------------------------
# Root health check
# -------------------------------------------------------
@app.get("/")
async def root():
    return {"success": True, "message": "Calculator API is running 🚀"}