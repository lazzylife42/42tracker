import models
import logging
from fastapi import FastAPI, HTTPException, Depends
from typing import Annotated
from database import engine, SessionLocal
from sqlalchemy import text
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

app = FastAPI()
models.BASE.metadata.create_all(bind=engine)

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
	