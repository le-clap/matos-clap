from pathlib import Path

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute
from fastapi.staticfiles import StaticFiles

from core.config import settings
from routers import auth, catalogs, categories, data_io, items, loans, requests, users


def _unique_id(route: APIRoute) -> str:
    """Defines a more readable unique ID for this API route."""
    tag = f"{route.tags[0]}_" if len(route.tags) > 0 else ""
    return tag + route.name


def _production() -> bool:
    """Returns True if the app is running in production mode."""
    return settings.ENV == "production"


app = FastAPI(
    title="MATOS CLAP",
    version="1.0.0",
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
