from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime, timezone

app = FastAPI()


class SensorData(BaseModel):
    sensor_id: str
    value: float
    timestamp: str


@app.get("/")
def root():
    return {"message": "Edge node alive"}


@app.post("/data")
def receive_data(data: SensorData):
    return {
        "received": data,
        "processed_at": datetime.now(timezone.utc).isoformat(),
    }
