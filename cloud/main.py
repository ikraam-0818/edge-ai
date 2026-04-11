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

app = FastAPI(title="Safety Monitor Cloud API")

engine = create_engine("sqlite:///safety_monitor.db")
Base = declarative_base()
Session = sessionmaker(bind=engine)

class Reading(Base):
    __tablename__ = "readings"
    id              = Column(Integer, primary_key=True, index=True)
    timestamp       = Column(DateTime, default=datetime.utcnow)
    helmet_detected = Column(Boolean, default=False)
    vest_detected   = Column(Boolean, default=False)
    gas_ppm         = Column(Float,   nullable=True)
    temperature_c   = Column(Float,   nullable=True)
    humidity_pct    = Column(Float,   nullable=True)
    vibration_g     = Column(Float,   nullable=True)
    is_safe         = Column(Boolean, default=True)
    alert_level     = Column(String,  default="SAFE")
    alert_reasons   = Column(String,  default="[]")

class Command(Base):
    __tablename__ = "commands"
    id        = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    command   = Column(String)
    payload   = Column(String)
    delivered = Column(Boolean, default=False)

Base.metadata.create_all(engine)

class SensorPayload(BaseModel):
    helmet_detected: bool          = False
    vest_detected:   bool          = False
    gas_ppm:         Optional[float] = None
    temperature_c:   Optional[float] = None
    humidity_pct:    Optional[float] = None
    vibration_g:     Optional[float] = None
    is_safe:         bool          = True
    alert_level:     str           = "SAFE"
    alert_reasons:   list          = []

class CommandPayload(BaseModel):
    command: str
    payload: dict = {}

anomaly_model    = IsolationForest(contamination=0.1, random_state=42)
_model_trained   = False
_training_buffer = []

def update_anomaly_model(reading):
    global _model_trained, _training_buffer
    features = [
        reading.gas_ppm       or 0,
        reading.temperature_c or 25,
        reading.vibration_g   or 0,
    ]
    _training_buffer.append(features)
    if len(_training_buffer) >= 50:
        X = np.array(_training_buffer[-200:])
        anomaly_model.fit(X)
        _model_trained = True

def predict_anomaly(reading):
    if not _model_trained:
        return {"score": None, "is_anomaly": False, "trained": False}
    features   = np.array([[
        reading.gas_ppm       or 0,
        reading.temperature_c or 25,
        reading.vibration_g   or 0,
    ]])
    score      = float(anomaly_model.score_samples(features)[0])
    is_anomaly = anomaly_model.predict(features)[0] == -1
    return {"score": round(score, 4), "is_anomaly": bool(is_anomaly), "trained": True}

@app.get("/")
def root():
    return {"status": "Safety Monitor Cloud API running"}

@app.post("/readings")
def receive_reading(data: SensorPayload):
    db = Session()
    reading = Reading(
        helmet_detected = data.helmet_detected,
        vest_detected   = data.vest_detected,
        gas_ppm         = data.gas_ppm,
        temperature_c   = data.temperature_c,
        humidity_pct    = data.humidity_pct,
        vibration_g     = data.vibration_g,
        is_safe         = data.is_safe,
        alert_level     = data.alert_level,
        alert_reasons   = json.dumps(data.alert_reasons),
    )
    db.add(reading)
    db.commit()
    db.refresh(reading)
    update_anomaly_model(reading)
    anomaly = predict_anomaly(reading)
    db.close()
    return {"id": reading.id, "received": True, "anomaly": anomaly}

@app.get("/readings/latest")
def get_latest(limit: int = 60):
    db   = Session()
    rows = db.query(Reading).order_by(Reading.id.desc()).limit(limit).all()
    db.close()
    return [
        {
            "id":              r.id,
            "timestamp":       r.timestamp.isoformat(),
            "helmet_detected": r.helmet_detected,
            "vest_detected":   r.vest_detected,
            "gas_ppm":         r.gas_ppm,
            "temperature_c":   r.temperature_c,
            "humidity_pct":    r.humidity_pct,
            "vibration_g":     r.vibration_g,
            "is_safe":         r.is_safe,
            "alert_level":     r.alert_level,
            "alert_reasons":   json.loads(r.alert_reasons or "[]"),
        }
        for r in reversed(rows)
    ]

@app.get("/stats")
def get_stats():
    db     = Session()
    total  = db.query(Reading).count()
    unsafe = db.query(Reading).filter(Reading.is_safe == False).count()
    latest = db.query(Reading).order_by(Reading.id.desc()).first()
    db.close()
    return {
        "total_readings": total,
        "unsafe_count":   unsafe,
        "safe_pct":       round((1 - unsafe / max(total, 1)) * 100, 1),
        "current_status": latest.alert_level if latest else "UNKNOWN",
    }

@app.post("/commands")
def send_command(cmd: CommandPayload):
    db = Session()
    c  = Command(command=cmd.command, payload=json.dumps(cmd.payload))
    db.add(c)
    db.commit()
    db.refresh(c)
    db.close()
    return {"id": c.id, "queued": True}

@app.get("/commands/pending")
def get_pending_commands():
    db   = Session()
    cmds = db.query(Command).filter(Command.delivered == False).all()
    for c in cmds:
        c.delivered = True
    db.commit()
    db.close()
    return [
        {
            "id":      c.id,
            "command": c.command,
            "payload": json.loads(c.payload),
        }
        for c in cmds
    ]