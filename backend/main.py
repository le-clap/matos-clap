from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute
from fastapi.staticfiles import StaticFiles

from core.config import settings
from routers import catalogs, categories, data_io, items, loans, requests, users
from routers.auth import router as auth_router


def _unique_id(route: APIRoute) -> str:
    """Defines a more readable unique ID for this API route."""
    tag = f"{route.tags[0]}_" if len(route.tags) > 0 else ""
    return tag + route.name


app = FastAPI(
    title="MATOS CLAP",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
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

if settings.ENV == "production":
    app.frontend("/", directory="../frontend/dist")


@app.get("/health")
def health_check():
    return {"status": "System Online"}


app.include_router(auth_router, prefix=settings.API_PREFIX)
app.include_router(categories.router, prefix=settings.API_PREFIX)
app.include_router(catalogs.router, prefix=settings.API_PREFIX)
app.include_router(items.router, prefix=settings.API_PREFIX)
app.include_router(users.router, prefix=settings.API_PREFIX)
app.include_router(requests.router, prefix=settings.API_PREFIX)
app.include_router(loans.router, prefix=settings.API_PREFIX)
app.include_router(data_io.router, prefix=settings.API_PREFIX)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
