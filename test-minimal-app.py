from fastapi import FastAPI

app = FastAPI()

@app.get("/test")
async def test():
    return {"message": "test working"}

@app.get("/auth/github/authorize")
@app.head("/auth/github/authorize")
async def auth_test():
    return {"message": "auth route working"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
