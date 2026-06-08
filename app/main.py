import logging
import models
import schemas
from fastapi import FastAPI, HTTPException, Depends
from typing import Annotated
from database import engine, SessionLocal
from sync import sync_projects
from sqlalchemy import text
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
	logger.info("Starting up -- creating tables")
	models.BASE.metadata.create_all(bind=engine)
	logger.info("Tables created -- app ready")
	yield
	logger.info("Shutting down -- disposing engine")
	engine.dispose()

app = FastAPI(lifespan=lifespan)

def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@app.get("/health")
async def health_check(db: db_dependency):
	try:
		db.execute(text("SELECT 1"))
		return {200:"Ok"}
	
	except Exception as e:
		logger.error(f"Database unreachable: {e}")
		raise HTTPException(status_code=500, detail="Database unreachable")
	

@app.get("/api/projects/", response_model=list[schemas.ProjectResponse])
async def get_projects(db: db_dependency):
	projets = db.query(models.Projects_42).all()
	return projets

@app.get("/api/42/sync")
async def sync_42(db: db_dependency):
    return sync_projects(db)