# InspiLarder - Project Knowledge Base

**Generated:** 2026-03-11 14:51 CST  
**Commit:** be583ae  
**Branch:** master

## OVERVIEW
AI-powered food management assistant (灵感食仓). FastAPI backend + vanilla HTML/JS frontend. Monolithic deployment - backend serves frontend directly on port 8000.

## STRUCTURE
```
InspiLarder/
├── backend/              # FastAPI + SQLAlchemy 2.0 (async)
│   ├── app/              # Main application code
│   │   ├── api/v1/       # API routes (auth, food, ai, admin, recipes)
│   │   ├── core/         # Config, security, logging
│   │   ├── models/       # SQLAlchemy ORM models
│   │   ├── schemas/      # Pydantic validation schemas
│   │   ├── services/     # Business logic (AI, image processing)
│   │   └── db/           # Database session/engine
│   ├── database/         # MySQL init.sql
│   └── uploads/          # User uploaded images
├── frontend/             # Static HTML/CSS/JS (served by backend)
│   ├── index.html        # SPA entry
│   └── js/app.js         # 4000+ line monolithic client app
└── deploy/               # Systemd service config
```

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| API routes | `backend/app/api/v1/` | auth.py, food.py, ai.py, admin.py, recipe.py, location.py |
| Data models | `backend/app/models/` | user.py, food.py, recipe.py, location.py |
| Pydantic schemas | `backend/app/schemas/` | Request/response DTOs |
| Business logic | `backend/app/services/` | ai_service.py, image_service.py |
| Config | `backend/app/core/config.py` | Pydantic Settings, OpenAI config |
| Frontend logic | `frontend/js/app.js` | All client-side code (4000+ lines) |
| Database | `backend/database/init.sql` | MySQL schema + seed data |
| Entry point | `backend/app/main.py` | FastAPI app, CORS, static files |

## CONVENTIONS
- **Async SQLAlchemy 2.0** with `aiomysql` driver
- **Pydantic v2** for validation and settings
- **JWT auth** with 7-day token expiry (HS256)
- **API versioning** via `/api/v1/` prefix
- **No frontend build** - Tailwind CSS via CDN
- **File uploads** stored in `backend/uploads/`
- **Database** MySQL with `utf8mb4_unicode_ci`

## ANTI-PATTERNS (THIS PROJECT)
- Duplicate class definitions in `backend/app/schemas/user.py` (Token, TokenPayload, UserLogin defined 4x)
- Duplicate DATABASE_URL in `backend/app/core/config.py` (lines 18, 20)
- Hardcoded default SECRET_KEY (must use env var in production)
- Default admin password `admin123` in init.sql
- `print()` instead of logging in main.py
- No tests implemented (pytest in requirements but no test files)

## UNIQUE STYLES
- **Dual OpenAI models**: Vision (gpt-4o) for image recognition, Text (gpt-4o-mini) for recipes
- **Monolithic serving**: FastAPI serves frontend SPA directly (no separate frontend server)
- **Vanilla JS frontend**: No React/Vue, all logic in single `app.js` file
- **Custom temperature settings**: Separate VISION_TEMPERATURE (0.2) and TEXT_TEMPERATURE (0.7)
- **Chinese-first UI**: All user-facing text in Chinese

## COMMANDS
```bash
# Development
cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production
cd backend && gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app -b 0.0.0.0:8000

# Database init
mysql -u root -p < backend/database/init.sql

# Code quality
ruff check --fix .
ruff format .
mypy .
```

## NOTES
- Frontend uses Lucide icons (deprecated `icon-name` attribute warning)
- Default admin: `admin` / `admin123`
- API docs: http://localhost:8000/api/docs (Swagger)
- Health check: http://localhost:8000/health
- Upload limit: 10MB, allowed types: jpeg, png, webp, gif
