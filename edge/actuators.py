class ActuatorManager:
    def __init__(self, red_pin=23, green_pin=24, buzzer_pin=22):
        print("ActuatorManager: running without physical actuators.")
        self.red_led = None
        self.green_led = None
        self.buzzer = None

    def trigger_alarm(self):
        print("[ALARM] Unsafe condition detected.")

    def set_state_safe(self):
        print("[SAFE] System state: safe.")

if __name__ == "__main__":
    ac = ActuatorManager()
    ac.trigger_alarm()
    ac.set_state_safe()
    print("Test complete.")
