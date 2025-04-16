from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..models import SessionLocal, Function
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class FunctionCreate(BaseModel):
    name: str
    runtime: str
    code: str
    route: str
    timeout: float = 30.0

class FunctionResponse(BaseModel):
    id: int
    name: str
    runtime: str
    route: str
    timeout: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/functions/", response_model=FunctionResponse)
def create_function(function: FunctionCreate, db: Session = Depends(get_db)):
    db_function = Function(
        name=function.name,
        runtime=function.runtime,
        code=function.code,
        route=function.route,
        timeout=function.timeout
    )
    db.add(db_function)
    db.commit()
    db.refresh(db_function)
    return db_function

@router.get("/functions/", response_model=List[FunctionResponse])
def list_functions(db: Session = Depends(get_db)):
    return db.query(Function).all()

@router.get("/functions/{function_id}", response_model=FunctionResponse)
def get_function(function_id: int, db: Session = Depends(get_db)):
    function = db.query(Function).filter(Function.id == function_id).first()
    if function is None:
        raise HTTPException(status_code=404, detail="Function not found")
    return function

@router.delete("/functions/{function_id}")
def delete_function(function_id: int, db: Session = Depends(get_db)):
    function = db.query(Function).filter(Function.id == function_id).first()
    if function is None:
        raise HTTPException(status_code=404, detail="Function not found")
    db.delete(function)
    db.commit()
    return {"message": "Function deleted"}
