# Backend Code Style Guidelines

This backend follows **PEP 8 — Python Code Style Guide**, with a few project-specific conventions.

## Official References

- [PEP 8 — Python Code Style Guide](https://peps.python.org/pep-0008/)
- [PEP 257 — Docstring Conventions](https://peps.python.org/pep-0257/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)

## Naming

| Kind | Rule | Example |
|------|------|---------|
| Module files | lowercase + underscores | `calculator.py`, `db.py` |
| Classes | PascalCase | `ExpressionError`, `CalculateRequest` |
| Functions / methods | snake_case | `calculate()`, `save_history()` |
| Constants | UPPERCASE + underscores | `DB_PATH`, `CREATE_TABLE_SQL` |
| Variables | snake_case | `result_str`, `postfix` |
| Private members | single leading underscore | `_get_conn()`, `_validate_chars()` |

## Indentation & Line Width

- **4 spaces** — never tabs
- Max **88 characters** per line (Black default)
- Spaces around binary operators: `a + b`, but **no** space before a unary minus: `-3`
- Space after commas: `(1, 2, 3)`

## Quotes

- Prefer **double quotes** for ordinary strings: `"expression"`
- Use double quotes consistently for dict keys
- Docstrings use triple quotes: `"""..."""`

## Import Order (groups separated by blank lines)

```python
# 1. Python stdlib
import os
import sqlite3

# 2. Third-party
from fastapi import FastAPI, HTTPException

# 3. Local modules
from src.calculator import calculate
```

## Comments

- Inline comments start with `# ` (hash + space)
- Comment **why**, not **what**
- Public functions / classes must have a docstring (Google or reST style — both OK)

Example (Google-style docstring):

```python
def calculate(expression: str) -> float:
    """Evaluate a math expression.

    Full pipeline: character validation → tokenize → parenthesis check →
    convert to postfix → evaluate.

    Args:
        expression: User-supplied math expression string.

    Returns:
        Result as a float.

    Raises:
        ExpressionError: Syntax error or illegal characters.
        DivideByZeroError: Division by zero.
    """
```

## Type Hints

- All functions should use **Python 3.9+ type annotations**
- FastAPI Pydantic models paired with annotations auto-generate API docs

```python
def save_history(expression: str, result: str) -> None:
    ...
```

## Exception Handling

- Custom business exceptions inherit from `ExpressionError`
- API layer catches and returns friendly JSON — never leak tracebacks to clients
- Never use bare `except:`; always name a concrete exception type

## Security Red Lines

- ❌ **Never** use `eval()` / `exec()` on user input
- ❌ **Never** concatenate SQL strings — always use parameterized queries with `?`
- ❌ **Never** expose sensitive info in logs or responses

## Recommended Tools

- Formatting: `black`, `isort`
- Linting: `ruff`, `flake8`
- Type checking: `mypy`