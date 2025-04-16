from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..models import SessionLocal, FunctionMetrics
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class MetricsCreate(BaseModel):
    function_id: int
    execution_time: float
    memory_usage: float
    status: str
    error_message: str = None

class MetricsResponse(BaseModel):
    id: int
    function_id: int
    execution_time: float
    memory_usage: float
    status: str
    error_message: str = None
    timestamp: datetime

    class Config:
        from_attributes = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/metrics/", response_model=MetricsResponse)
def create_metrics(metrics: MetricsCreate, db: Session = Depends(get_db)):
    db_metrics = FunctionMetrics(
        function_id=metrics.function_id,
        execution_time=metrics.execution_time,
        memory_usage=metrics.memory_usage,
        status=metrics.status,
        error_message=metrics.error_message
    )
    db.add(db_metrics)
    db.commit()
    db.refresh(db_metrics)
    return db_metrics

@router.get("/metrics/function/{function_id}", response_model=List[MetricsResponse])
def get_function_metrics(function_id: int, db: Session = Depends(get_db)):
    return db.query(FunctionMetrics).filter(FunctionMetrics.function_id == function_id).all()

@router.get("/metrics/stats/function/{function_id}")
def get_function_stats(function_id: int, db: Session = Depends(get_db)):
    metrics = db.query(FunctionMetrics).filter(FunctionMetrics.function_id == function_id).all()
    
    if not metrics:
        return {
            "total_executions": 0,
            "avg_execution_time": 0,
            "avg_memory_usage": 0,
            "success_rate": 0,
            "error_rate": 0
        }
    
    total = len(metrics)
    successes = len([m for m in metrics if m.status == "success"])
    
    return {
        "total_executions": total,
        "avg_execution_time": sum(m.execution_time for m in metrics) / total,
        "avg_memory_usage": sum(m.memory_usage for m in metrics) / total,
        "success_rate": (successes / total) * 100,
        "error_rate": ((total - successes) / total) * 100
    }
