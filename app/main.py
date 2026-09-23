from fastapi import FastAPI

app=FastAPI(title="Cab Pooling & Smart Pickup Routing")

@app.get("/health")
def health_check():
    return {"status":"ok"}