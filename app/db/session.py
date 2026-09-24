from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import DATABASE_URL
import app.db.models

engine = create_engine(DATABASE_URL)

SessionFactory = sessionmaker(bind=engine)


def get_db():

    db = SessionFactory()

    try:
        yield db

    finally:
        db.close()
