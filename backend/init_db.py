from backend.models.base import Base, engine
from backend.models.function import Function
from backend.models.metrics import FunctionMetrics

def init_db():
    # Create all tables
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")
