import time
import board
import adafruit_dht
from gpiozero import Button

class SensorManager:
    def __init__(self):
        print("Initializing SensorManager...")
        try:
            self.dht = adafruit_dht.DHT22(board.D4)
            self.vibration = Button(17)
            self.gas = Button(27)
            print("SensorManager initialized successfully.")
        except Exception as e:
            print(f"Warning: Could not initialize sensors. Error: {e}")
            self.dht = None
            self.vibration = None
            self.gas = None

    def read_environment(self):
        """Returns Temperature in C and Humidity percentage from DHT22."""
        try:
            return {
                "temperature": self.dht.temperature,
                "humidity": self.dht.humidity
            }
        except RuntimeError as e:
            print(f"DHT22 read error: {e}")
            return {"temperature": None, "humidity": None}

    def read_vibration(self):
        """Returns vibration detected state with debounce to avoid false triggers."""
        try:
        # Sample 3 times over 0.1s to confirm real vibration
            detections = 0
            for _ in range(3):
                if self.vibration.is_pressed:
                    detections += 1
                time.sleep(0.03)
            return {
                "vibration_detected": detections >= 3
            }
        except Exception as e:
            print(f"Vibration read error: {e}")
            return {"vibration_detected": False}

    def read_gas(self):
        """Returns gas detected state from MQ135 digital output."""
        try:
            return {
                "gas_detected": self.gas.is_pressed,
                "ppm": 500.0 if self.gas.is_pressed else 50.0
            }
        except Exception as e:
            print(f"Gas read error: {e}")
            return {"gas_detected": False, "ppm": 0.0}

if __name__ == "__main__":
    sm = SensorManager()
    while True:
        print(sm.read_environment())
        print(sm.read_vibration())
        print(sm.read_gas())
        time.sleep(2)
