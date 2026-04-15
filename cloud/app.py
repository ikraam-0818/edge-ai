from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, Float, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from typing import Optional
import json
import numpy as np
from sklearn.ensemble import IsolationForest
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import threading

app = FastAPI(title="Safety Monitor Cloud API")

# ── Database Setup ─────────────────────────────────────────────────
engine = create_engine("sqlite:///safety_monitor.db", connect_args={"check_same_thread": False})
Base = declarative_base()
Session = sessionmaker(bind=engine)

class Reading(Base):
    __tablename__ = "readings"
    id           = Column(Integer, primary_key=True, index=True)
    timestamp    = Column(DateTime, default=datetime.utcnow)
    temperature  = Column(Float, nullable=True)
    humidity     = Column(Float, nullable=True)
    vibration    = Column(String, default="Normal")
    person_count = Column(Integer, default=0)
    helmet_count = Column(Integer, default=0)
    violations   = Column(Integer, default=0)
    alert        = Column(Boolean, default=False)
    is_anomaly   = Column(Boolean, default=False)

Base.metadata.create_all(engine)

# ── Pydantic Models ────────────────────────────────────────────────
class CommandPayload(BaseModel):
    command: str
    payload: dict = {}

# ── AI Model Setup (Isolation Forest) ──────────────────────────────
anomaly_model    = IsolationForest(contamination=0.1, random_state=42)
_model_trained   = False
_training_buffer = []

def process_anomaly(reading):
    global _model_trained, _training_buffer
    
    # Feature extraction (using temp, humidity, and converting vibration to a number)
    vib_score = 1.0 if reading.vibration != "Normal" else 0.0
    features = [reading.temperature or 0, reading.humidity or 0, vib_score]
    
    _training_buffer.append(features)
    
    # Train if we have enough data
    if len(_training_buffer) >= 50:
        X = np.array(_training_buffer[-200:])
        anomaly_model.fit(X)
        _model_trained = True

    # Predict
    if _model_trained:
        X_pred = np.array([features])
        is_anomaly = anomaly_model.predict(X_pred)[0] == -1
        return bool(is_anomaly)
    return False

# ── AWS IoT Configuration & MQTT ───────────────────────────────────
ENDPOINT = "a1cwlyvzluprga-ats.iot.eu-north-1.amazonaws.com"
CLIENT_ID = "EdgePi-Cloud-DB"
TOPIC_SUB = "edge-ai/telemetry"
TOPIC_PUB = "edge-ai/commands"

mqtt_client = AWSIoTMQTTClient(CLIENT_ID)

def on_mqtt_message(client, userdata, message):
    try:
        data = json.loads(message.payload.decode('utf-8'))
        
        db = Session()
        reading = Reading(
            temperature  = data.get("temperature"),
            humidity     = data.get("humidity"),
            vibration    = data.get("vibration", "Normal"),
            person_count = data.get("person_count", 0),
            helmet_count = data.get("helmet_count", 0),
            violations   = data.get("violations", 0),
            alert        = data.get("alert", False)
        )
        
        # Run AI Anomaly check
        reading.is_anomaly = process_anomaly(reading)
        
        db.add(reading)
        db.commit()
        db.close()
        print(f"Saved to DB: {data}")
    except Exception as e:
        print(f"Error processing MQTT message: {e}")

def start_mqtt():
    mqtt_client.configureEndpoint(ENDPOINT, 8883)
    mqtt_client.configureCredentials("/home/ubuntu/certs/AmazonRootCA1.pem", "/home/ubuntu/certs/device.key", "/home/ubuntu/certs/device.crt")
    mqtt_client.connect()
    mqtt_client.subscribe(TOPIC_SUB, 1, on_mqtt_message)
    print("MQTT Connected and Subscribed.")

# Start MQTT in background thread
threading.Thread(target=start_mqtt, daemon=True).start()

# ── API Endpoints ──────────────────────────────────────────────────
@app.get("/")
def root():
    return {"status": "Safety Monitor Cloud API running"}

@app.get("/readings/latest")
def get_latest(limit: int = 60):
    db   = Session()
    rows = db.query(Reading).order_by(Reading.id.desc()).limit(limit).all()
    db.close()
    return [
        {
            "id":           r.id,
            "timestamp":    r.timestamp.isoformat(),
            "temperature":  r.temperature,
            "humidity":     r.humidity,
            "vibration":    r.vibration,
            "person_count": r.person_count,
            "helmet_count": r.helmet_count,
            "violations":   r.violations,
            "alert":        r.alert,
            "is_anomaly":   r.is_anomaly
        }
        for r in reversed(rows)
    ]

@app.get("/stats")
def get_stats():
    db     = Session()
    total  = db.query(Reading).count()
    unsafe = db.query(Reading).filter(Reading.alert == True).count()
    db.close()
    
    safe_pct = round((1 - unsafe / max(total, 1)) * 100, 1) if total > 0 else 100.0
    
    return {
        "total_readings": total,
        "unsafe_count":   unsafe,
        "safe_pct":       safe_pct
    }

@app.post("/commands")
def send_command(cmd: CommandPayload):
    # Instead of saving to a local DB, we publish directly to the EdgePi via AWS IoT
    payload_str = json.dumps({"command": cmd.command, "payload": cmd.payload})
    try:
        mqtt_client.publish(TOPIC_PUB, payload_str, 1)
        return {"status": "Command published to MQTT", "delivered": True}
    except Exception as e:
        return {"status": "Failed to publish", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)