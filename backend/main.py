from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute

from core.config import settings
from db.seed import seed_data
from routers import catalogs, categories, items, loans, requests, users
from routers.auth import router as auth_router


def _unique_id(route: APIRoute) -> str:
    """Defines a more readable unique ID for this API route."""
    tag = f"{route.tags[0]}_" if len(route.tags) > 0 else ""
    return tag + route.name


@asynccontextmanager
async def lifespan(_: FastAPI):
    print("Starting up...")
    seed_data()

    yield

    print("Shutting down...")


app = FastAPI(
    # lifespan=lifespan,
    title="MATOS CLAP",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    generate_unique_id_function=_unique_id,
)

app.add_middleware(
    CORSMiddleware,  # ty: ignore[invalid-argument-type]
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"status": "System Online"}


app.include_router(auth_router, prefix=settings.API_PREFIX)
app.include_router(categories.router, prefix=settings.API_PREFIX)
app.include_router(catalogs.router, prefix=settings.API_PREFIX)
app.include_router(items.router, prefix=settings.API_PREFIX)
app.include_router(users.router, prefix=settings.API_PREFIX)
app.include_router(requests.router, prefix=settings.API_PREFIX)
app.include_router(loans.router, prefix=settings.API_PREFIX)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
