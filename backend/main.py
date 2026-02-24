from contextlib import asynccontextmanager

from fastapi import FastAPI

from core.config import settings
from db.database import create_tables
from db.seed import seed_data
from routers import catalogs, categories, items, loans, requests, users


@asynccontextmanager
async def lifespan(_: FastAPI):
    print("Initializing db...")
    create_tables()
    seed_data()

    yield

    print("Shutting down...")


app = FastAPI(
    # lifespan=lifespan,
    title="MATOS CLAP",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=settings.ALLOWED_ORIGINS,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


@app.get("/")
def read_root():
    return {"status": "System Online"}


app.include_router(categories.router, prefix=settings.API_PREFIX)
app.include_router(catalogs.router, prefix=settings.API_PREFIX)
app.include_router(items.router, prefix=settings.API_PREFIX)
app.include_router(users.router, prefix=settings.API_PREFIX)
app.include_router(requests.router, prefix=settings.API_PREFIX)
app.include_router(loans.router, prefix=settings.API_PREFIX)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
