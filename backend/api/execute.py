from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..models import SessionLocal, Function, FunctionMetrics
from ..executor.docker.executor import DockerExecutor
import time

router = APIRouter()
executor = DockerExecutor()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/execute/{function_id}")
async def execute_function(function_id: int, db: Session = Depends(get_db)):
    # Get function
    function = db.query(Function).filter(Function.id == function_id).first()
    if not function:
        raise HTTPException(status_code=404, detail="Function not found")
    
    # Execute function
    start_time = time.time()
    try:
        result = executor.execute(
            code=function.code,
            runtime=function.runtime,
            timeout=function.timeout
        )
        execution_time = time.time() - start_time
        
        # Record metrics
        metrics = FunctionMetrics(
            function_id=function_id,
            execution_time=execution_time,
            memory_usage=0.0,  # TODO: Implement memory tracking
            status="success" if result["status"] == "success" else "error",
            error_message=result["output"] if result["status"] == "error" else None
        )
        db.add(metrics)
        db.commit()
        
        return {
            "status": result["status"],
            "output": result["output"],
            "execution_time": execution_time
        }
        
    except Exception as e:
        execution_time = time.time() - start_time
        # Record error metrics
        metrics = FunctionMetrics(
            function_id=function_id,
            execution_time=execution_time,
            memory_usage=0.0,
            status="error",
            error_message=str(e)
        )
        db.add(metrics)
        db.commit()
        
        raise HTTPException(status_code=500, detail=str(e))
