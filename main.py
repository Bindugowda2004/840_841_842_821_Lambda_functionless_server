from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Serverless Platform")

@app.get("/")
async def root():
    return {"message": "Welcome to the Serverless Platform"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
