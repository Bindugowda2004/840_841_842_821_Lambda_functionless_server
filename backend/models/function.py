from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Function(Base):
    __tablename__ = "functions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    runtime = Column(String)  # python or javascript
    code = Column(String)
    route = Column(String, unique=True)
    timeout = Column(Float, default=30.0)  # timeout in seconds
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship with metrics
    metrics = relationship("FunctionMetrics", back_populates="function", cascade="all, delete-orphan")
