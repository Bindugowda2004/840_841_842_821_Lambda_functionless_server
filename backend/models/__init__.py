from .base import Base, engine, SessionLocal
from .function import Function

# Create all tables
Base.metadata.create_all(bind=engine)
