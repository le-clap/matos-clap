from sqlmodel import Session, create_engine

from core.config import settings

engine = create_engine(settings.DATABASE_URL, echo=settings.DEBUG)


def get_session():
    with Session(engine, autocommit=False, autoflush=False) as session:
        yield session
