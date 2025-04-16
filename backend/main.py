from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import functions, metrics

app = FastAPI(title="Serverless Platform")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(functions.router, prefix="/api/v1", tags=["functions"])
app.include_router(metrics.router, prefix="/api/v1", tags=["metrics"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Serverless Platform"}
