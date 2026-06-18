from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime, timezone

app = FastAPI()

# Riba, kurią viršijus reikšmė pažymima kaip alertas
THRESHOLD = 30.0

# Statistika atmintyje kiekvienam sensoriui: sensor_id -> {"count", "sum"}
stats = {}


class SensorData(BaseModel):
    sensor_id: str
    value: float
    timestamp: str


@app.get("/")
def root():
    return {"message": "Edge node alive"}


@app.post("/data")
def receive_data(data: SensorData):
    s = stats.setdefault(data.sensor_id, {"count": 0, "sum": 0.0})
    s["count"] += 1
    s["sum"] += data.value
    running_average = s["sum"] / s["count"]

    return {
        "sensor_id": data.sensor_id,
        "value": data.value,
        "running_average": round(running_average, 2),
        "count": s["count"],
        "alert": data.value > THRESHOLD,
        "processed_at": datetime.now(timezone.utc).isoformat(),
    }
