from sqlalchemy import Column, Integer, Float, DateTime, String, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class FunctionMetrics(Base):
    __tablename__ = "function_metrics"

    id = Column(Integer, primary_key=True, index=True)
    function_id = Column(Integer, ForeignKey("functions.id"))
    execution_time = Column(Float)  # in seconds
    memory_usage = Column(Float)    # in MB
    status = Column(String)         # success or error
    error_message = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationship
    function = relationship("Function", back_populates="metrics")
