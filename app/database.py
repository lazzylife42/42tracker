import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

load_dotenv()

HOSTNAME = os.getenv('HOST')
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')

URL_DATABASE = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{HOSTNAME}:5432/postgres_db'
engine = create_engine(URL_DATABASE)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class BASE(DeclarativeBase):
    pass