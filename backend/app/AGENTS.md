# Backend App - Application Code

**Scope:** FastAPI application logic for InspiLarder

## OVERVIEW
Main FastAPI application: routes, models, schemas, services, and configuration.

## STRUCTURE
```
app/
├── api/v1/       # Route handlers (auth, food, ai, admin, recipe, location)
├── api/deps.py   # Dependency injection (get_current_user, get_db)
├── core/         # Config, security (JWT), logging
├── models/       # SQLAlchemy ORM models
├── schemas/      # Pydantic request/response DTOs
├── services/     # Business logic (AI, image processing)
├── db/           # Async session, engine, base
└── main.py       # FastAPI app factory
```

## WHERE TO LOOK
| Task | File | Notes |
|------|------|-------|
| Add API endpoint | `api/v1/<domain>.py` | Register in `api/v1/router.py` |
| New data model | `models/<domain>.py` | Import in `models/__init__.py` |
| Request/response schema | `schemas/<domain>.py` | Pydantic v2, `ConfigDict(from_attributes=True)` |
| Auth dependency | `api/deps.py` | `get_current_user`, `get_current_superuser` |
| AI features | `services/ai_service.py` | Dual model: vision (gpt-4o) + text (gpt-4o-mini) |
| Image upload | `services/image_service.py` | Pillow processing, 10MB limit |
| DB session | `db/session.py` | `get_db()` generator for DI |
| Config/env vars | `core/config.py` | Pydantic Settings, `.env` file |

## CONVENTIONS
- **Lazy initialization**: DB engine created on first access (singleton pattern)
- **Separate temperatures**: `VISION_TEMPERATURE=0.2`, `TEXT_TEMPERATURE=0.7`
- **7-day JWT expiry**: `ACCESS_TOKEN_EXPIRE_MINUTES=10080`
- **Commit on yield**: `get_db()` auto-commits on success, rollback on exception

## ANTI-PATTERNS
- `schemas/user.py`: Token, TokenPayload, UserLogin defined **5 times** (lines 195-385) — DELETE duplicates
- `core/config.py`: DATABASE_URL defined **twice** (lines 18, 20) — DELETE one
- `main.py`: Uses `print()` instead of `logger` for startup messages
- Hardcoded `SECRET_KEY` default in config.py — must use env var in production
