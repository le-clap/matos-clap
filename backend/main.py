from pathlib import Path
from uuid import uuid4

import structlog
from fastapi import APIRouter, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from fastapi.staticfiles import StaticFiles

from core.config import settings
from core.logging import configure_logging
from routers import auth, catalogs, categories, data_io, items, loans, requests, users

configure_logging()

logger = structlog.get_logger(__name__)


def _unique_id(route: APIRoute) -> str:
    """Defines a more readable unique ID for this API route."""
    tag = f"{route.tags[0]}_" if len(route.tags) > 0 else ""
    return tag + route.name


def _production() -> bool:
    """Returns True if the app is running in production mode."""
    return settings.ENV == "production"


app = FastAPI(
    title="MATOS CLAP",
    version="1.0.2",
    openapi_url=None if _production() else "/openapi.json",
    docs_url=None if _production() else "/docs",
    redoc_url=None if _production() else "/redoc",
    generate_unique_id_function=_unique_id,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def bind_request_context(request: Request, call_next):
    """Tag every log line emitted during this request with a shared request_uuid."""
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(request_uuid=str(uuid4())[:8])
    return await call_next(request)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Log unhandled exceptions with a stack trace and return a generic 500."""
    logger.error("unhandled_exception", path=request.url.path, exc_info=exc)
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})


media_dir = Path(settings.MEDIA_DIR)
media_dir.mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=media_dir), name="media")


if _production():
    app.frontend("/", directory="static")


@app.get("/health")
def health_check():
    return {"status": "System Online"}


api_router = APIRouter(prefix="/api")
api_router.include_router(auth.router)
api_router.include_router(categories.router)
api_router.include_router(catalogs.router)
api_router.include_router(items.router)
api_router.include_router(users.router)
api_router.include_router(requests.router)
api_router.include_router(loans.router)
api_router.include_router(data_io.router)
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
