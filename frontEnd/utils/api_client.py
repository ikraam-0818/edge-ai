"""
API client for the Safety Monitor FastAPI backend.
All HTTP calls are centralised here with error handling.
"""
import requests
from typing import Optional

BASE_URL = "http://localhost:8000"
TIMEOUT  = 5   # seconds


# ---------------------------------------------------------------------------
# Connectivity
# ---------------------------------------------------------------------------

def health_check() -> bool:
    """Return True if the backend is reachable."""
    try:
        r = requests.get(f"{BASE_URL}/", timeout=TIMEOUT)
        return r.status_code == 200
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Data fetching
# ---------------------------------------------------------------------------

def get_stats() -> Optional[dict]:
    """
    Returns:
        {total_readings, unsafe_count, safe_pct, current_status}
    """
    try:
        r = requests.get(f"{BASE_URL}/stats", timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


def get_latest_readings(limit: int = 60) -> list[dict]:
    """
    Returns a list of reading dicts ordered oldest → newest.
    Each dict has: id, timestamp, helmet_detected, vest_detected,
    gas_ppm, temperature_c, humidity_pct, vibration_g,
    is_safe, alert_level, alert_reasons.
    """
    try:
        r = requests.get(f"{BASE_URL}/readings/latest", params={"limit": limit}, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except Exception:
        return []


def get_alerts(limit: int = 120) -> list[dict]:
    """Return only unsafe readings from the latest batch."""
    readings = get_latest_readings(limit)
    return [r for r in readings if not r.get("is_safe", True)]


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def send_command(command: str, payload: dict = {}) -> bool:
    """
    Queue a command for the edge device.
    Returns True on success.
    """
    try:
        r = requests.post(
            f"{BASE_URL}/commands",
            json={"command": command, "payload": payload},
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        return True
    except Exception:
        return False


def send_reading(data: dict) -> Optional[dict]:
    """
    POST a reading to the backend (used for testing / simulation).
    Returns the response dict on success, None on failure.
    """
    try:
        r = requests.post(f"{BASE_URL}/readings", json=data, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


def get_latest_frame() -> Optional[bytes]:
    """Fetch the latest JPEG camera frame. Returns bytes or None."""
    try:
        r = requests.get(f"{BASE_URL}/frame/latest", timeout=TIMEOUT)
        if r.status_code == 204:
            return None
        r.raise_for_status()
        return r.content
    except Exception:
        return None


def get_alert_frame() -> Optional[bytes]:
    """Fetch the last frame captured during an unsafe/violation event."""
    try:
        r = requests.get(f"{BASE_URL}/frame/alert", timeout=TIMEOUT)
        if r.status_code == 204:
            return None
        r.raise_for_status()
        return r.content
    except Exception:
        return None
