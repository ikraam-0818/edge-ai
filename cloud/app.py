from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, Float, String, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from typing import Optional, List
import json
import base64
import numpy as np
from sklearn.ensemble import IsolationForest
import threading

app = FastAPI(title="Safety Monitor Cloud API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Database Setup ─────────────────────────────────────────────────
engine = create_engine("sqlite:///safety_monitor.db", connect_args={"check_same_thread": False})
Base   = declarative_base()
Session = sessionmaker(bind=engine)

class Reading(Base):
    __tablename__ = "readings"
    id               = Column(Integer, primary_key=True, index=True)
    timestamp        = Column(DateTime, default=datetime.utcnow)
    helmet_detected  = Column(Boolean, default=False)
    vest_detected    = Column(Boolean, default=False)
    temperature_c    = Column(Float,   nullable=True)
    humidity_pct     = Column(Float,   nullable=True)
    gas_ppm          = Column(Float,   nullable=True)
    vibration_g      = Column(Float,   nullable=True)
    is_safe          = Column(Boolean, default=True)
    alert_level      = Column(String,  default="SAFE")
    alert_reasons    = Column(Text,    default="[]")   # JSON list
    is_anomaly       = Column(Boolean, default=False)

Base.metadata.create_all(engine)

# ── In-memory frames (JPEG bytes) ────────────────────────────────
_latest_frame: Optional[bytes] = None       # most recent frame always
_alert_frame:  Optional[bytes] = None       # last frame where is_safe=False
_frame_lock = threading.Lock()

# ── Pydantic Models ────────────────────────────────────────────────
class ReadingPayload(BaseModel):
    helmet_detected: bool  = False
    vest_detected:   bool  = False
    temperature_c:   Optional[float] = None
    humidity_pct:    Optional[float] = None
    gas_ppm:         Optional[float] = None
    vibration_g:     Optional[float] = None
    is_safe:         bool  = True
    alert_level:     str   = "SAFE"
    alert_reasons:   List[str] = []
    frame_b64:       Optional[str] = None   # base64-encoded JPEG from edge

class CommandPayload(BaseModel):
    command: str
    payload: dict = {}

# ── Anomaly Detection (Isolation Forest) ──────────────────────────
anomaly_model    = IsolationForest(contamination=0.1, random_state=42)
_model_trained   = False
_training_buffer: list = []

def _check_anomaly(temp, humidity, gas, vibration) -> bool:
    global _model_trained, _training_buffer
    features = [temp or 0, humidity or 0, gas or 0, vibration or 0]
    _training_buffer.append(features)
    if len(_training_buffer) >= 50:
        X = np.array(_training_buffer[-200:])
        anomaly_model.fit(X)
        _model_trained = True
    if _model_trained:
        return anomaly_model.predict(np.array([features]))[0] == -1
    return False

# ── AWS IoT / MQTT (optional — only active when certs are present) ─
try:
    from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

    ENDPOINT  = "a1cwlyvzluprga-ats.iot.eu-north-1.amazonaws.com"
    CLIENT_ID = "EdgePi-Cloud-DB"
    TOPIC_SUB = "edge-ai/telemetry"
    TOPIC_PUB = "edge-ai/commands"

    mqtt_client = AWSIoTMQTTClient(CLIENT_ID)

    def _on_mqtt_message(client, userdata, message):
        global _latest_frame
        try:
            data = json.loads(message.payload.decode("utf-8"))

            # Decode and cache latest camera frame if included
            frame_b64 = data.get("frame_b64")
            if frame_b64:
                decoded = base64.b64decode(frame_b64)
                with _frame_lock:
                    _latest_frame = decoded
                    if not data.get("is_safe", True):
                        _alert_frame = decoded

            db = Session()
            reasons = data.get("alert_reasons", [])
            r = Reading(
                helmet_detected = bool(data.get("helmet_detected", False)),
                vest_detected   = bool(data.get("vest_detected",   False)),
                temperature_c   = data.get("temperature_c"),
                humidity_pct    = data.get("humidity_pct"),
                gas_ppm         = data.get("gas_ppm"),
                vibration_g     = data.get("vibration_g"),
                is_safe         = bool(data.get("is_safe", True)),
                alert_level     = data.get("alert_level", "SAFE"),
                alert_reasons   = json.dumps(reasons),
                is_anomaly      = _check_anomaly(
                    data.get("temperature_c", 0),
                    data.get("humidity_pct",  0),
                    data.get("gas_ppm",       0),
                    data.get("vibration_g",   0),
                ),
            )
            db.add(r)
            db.commit()
            db.close()
        except Exception as e:
            print(f"MQTT handler error: {e}")

    def _start_mqtt():
        try:
            mqtt_client.configureEndpoint(ENDPOINT, 8883)
            mqtt_client.configureCredentials(
                "/home/ubuntu/certs/AmazonRootCA1.pem",
                "/home/ubuntu/certs/device.key",
                "/home/ubuntu/certs/device.crt",
            )
            mqtt_client.connect()
            mqtt_client.subscribe(TOPIC_SUB, 1, _on_mqtt_message)
            print("MQTT connected and subscribed.")
        except Exception as e:
            print(f"MQTT startup skipped: {e}")

    threading.Thread(target=_start_mqtt, daemon=True).start()
    _mqtt_available = True

except ImportError:
    _mqtt_available = False
    mqtt_client = None
    print("AWSIoTPythonSDK not installed — MQTT disabled.")


# ── Helpers ────────────────────────────────────────────────────────
def _reading_to_dict(r: Reading) -> dict:
    try:
        reasons = json.loads(r.alert_reasons or "[]")
    except Exception:
        reasons = []
    return {
        "id":               r.id,
        "timestamp":        r.timestamp.isoformat(),
        "helmet_detected":  r.helmet_detected,
        "vest_detected":    r.vest_detected,
        "temperature_c":    r.temperature_c,
        "humidity_pct":     r.humidity_pct,
        "gas_ppm":          r.gas_ppm,
        "vibration_g":      r.vibration_g,
        "is_safe":          r.is_safe,
        "alert_level":      r.alert_level,
        "alert_reasons":    reasons,
        "is_anomaly":       r.is_anomaly,
    }


# ── API Endpoints ──────────────────────────────────────────────────

@app.get("/")
def root():
    return {"status": "Safety Monitor Cloud API running"}


@app.get("/stats")
def get_stats():
    db     = Session()
    total  = db.query(Reading).count()
    unsafe = db.query(Reading).filter(Reading.is_safe == False).count()
    latest = db.query(Reading).order_by(Reading.id.desc()).first()
    db.close()

    safe_pct       = round((1 - unsafe / max(total, 1)) * 100, 1)
    current_status = latest.alert_level if latest else "UNKNOWN"

    return {
        "total_readings":  total,
        "unsafe_count":    unsafe,
        "safe_pct":        safe_pct,
        "current_status":  current_status,
    }


@app.get("/readings/latest")
def get_latest_readings(limit: int = 60):
    db   = Session()
    rows = db.query(Reading).order_by(Reading.id.desc()).limit(limit).all()
    db.close()
    return [_reading_to_dict(r) for r in reversed(rows)]


@app.post("/readings")
def post_reading(payload: ReadingPayload):
    """Accept a reading from the edge device or test simulation."""
    global _latest_frame

    if payload.frame_b64:
        decoded = base64.b64decode(payload.frame_b64)
        with _frame_lock:
            _latest_frame = decoded
            if not payload.is_safe:
                _alert_frame = decoded

    db = Session()
    r  = Reading(
        helmet_detected = payload.helmet_detected,
        vest_detected   = payload.vest_detected,
        temperature_c   = payload.temperature_c,
        humidity_pct    = payload.humidity_pct,
        gas_ppm         = payload.gas_ppm,
        vibration_g     = payload.vibration_g,
        is_safe         = payload.is_safe,
        alert_level     = payload.alert_level,
        alert_reasons   = json.dumps(payload.alert_reasons),
        is_anomaly      = _check_anomaly(
            payload.temperature_c or 0,
            payload.humidity_pct  or 0,
            payload.gas_ppm       or 0,
            payload.vibration_g   or 0,
        ),
    )
    db.add(r)
    db.commit()
    db.refresh(r)
    result = _reading_to_dict(r)
    anomaly_flag = {"is_anomaly": r.is_anomaly}
    db.close()
    return {"id": r.id, "anomaly": anomaly_flag, **result}


@app.get("/frame/latest")
def get_latest_frame():
    """Return the most recent camera frame as a JPEG image."""
    with _frame_lock:
        frame = _latest_frame
    if frame is None:
        return Response(status_code=204)
    return Response(content=frame, media_type="image/jpeg")


@app.get("/frame/alert")
def get_alert_frame():
    """Return the last frame captured during an unsafe event."""
    with _frame_lock:
        frame = _alert_frame
    if frame is None:
        return Response(status_code=204)
    return Response(content=frame, media_type="image/jpeg")


@app.post("/commands")
def send_command(cmd: CommandPayload):
    if _mqtt_available and mqtt_client:
        try:
            mqtt_client.publish(
                TOPIC_PUB,
                json.dumps({"command": cmd.command, "payload": cmd.payload}),
                1,
            )
            return {"status": "published", "delivered": True}
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    return {"status": "mqtt_unavailable", "delivered": False}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
