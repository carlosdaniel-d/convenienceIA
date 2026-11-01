from fastapi import FastAPI

app = FastAPI(title="convenienceIA")

@app.get("/")
def home():
    return {"status": "ok", "message": "convenienceIA está en línea"}
