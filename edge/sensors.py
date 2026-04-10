import time
import random # Placeholder for real I2C/GPIO reads

class SensorManager:
    def __init__(self):
        """
        Initializes the DHT22 and MPU6050 sensors. 
        MEMBER 2: Replace the dummy data generation with actual I2C/GPIO logic!
        """
        print("SensorManager initialized.")
        # E.g.: self.dht = adafruit_dht.DHT22(board.D4)
        
    def read_environment(self):
        """Returns Temperature in C and Humidity percentage."""
        # TODO: Implement real DHT22 bus reading
        return {
            "temperature": round(random.uniform(20.0, 45.0), 1),
            "humidity": round(random.uniform(40.0, 90.0), 1)
        }
        
    def read_vibration(self):
        """Returns XYZ acceleration from MPU6050."""
        # TODO: Implement real MPU6050 I2C reading
        # A simple magnitude check can determine if there's excessive vibration 
        return {
            "accel_x": round(random.uniform(-1.0, 1.0), 2),
            "accel_y": round(random.uniform(-1.0, 1.0), 2),
            "accel_z": round(random.uniform(9.0, 10.5), 2) # Near 9.8m/s^2 (gravity)
        }

# Mini-test for MEMBER 2
if __name__ == "__main__":
    sm = SensorManager()
    print(sm.read_environment())
    print(sm.read_vibration())
