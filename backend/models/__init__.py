from .base import Base, engine, SessionLocal
from .function import Function
from .metrics import FunctionMetrics
from .user import User

# Create all tables
Base.metadata.create_all(bind=engine)
