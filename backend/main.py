from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from .api import functions, metrics, auth, execute
from .api.auth import get_current_user

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
app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
app.include_router(
    functions.router,
    prefix="/api/v1",
    tags=["functions"],
    dependencies=[Depends(get_current_user)]
)
app.include_router(
    metrics.router,
    prefix="/api/v1",
    tags=["metrics"],
    dependencies=[Depends(get_current_user)]
)
app.include_router(
    execute.router,
    prefix="/api/v1",
    tags=["execute"],
    dependencies=[Depends(get_current_user)]
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Serverless Platform"}
