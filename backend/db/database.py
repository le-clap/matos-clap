from sqlmodel import Session, SQLModel, create_engine

from core.config import settings

engine = create_engine(settings.DATABASE_URL, echo=True)


def get_session():
    with Session(engine, autocommit=False, autoflush=False) as session:
        yield session


def create_tables():
    SQLModel.metadata.create_all(engine)
