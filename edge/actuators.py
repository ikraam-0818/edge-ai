from gpiozero import LED, Buzzer
import time

class ActuatorManager:
    def __init__(self, red_pin=17, green_pin=27, buzzer_pin=22):
        """
        Initializes the GPIO outputs for the LEDs and Buzzer on the Raspberry Pi.
        Pins are BCM numbering.
        """
        try:
            self.red_led = LED(red_pin)
            self.green_led = LED(green_pin)
            self.buzzer = Buzzer(buzzer_pin)
            print("Actuators initialized successfully.")
            
            # Initial state: Green Light, all clear.
            self.set_state_safe()
        except Exception as e:
            print(f"Warning: Could not initialize GPIO. Are you running this on a Pi? Error: {e}")
            self.red_led, self.green_led, self.buzzer = None, None, None

    def trigger_alarm(self):
        """Triggers the Red LED and activates the warning buzzer."""
        if self.red_led:
            self.green_led.off()
            self.red_led.on()
            self.buzzer.beep(on_time=0.5, off_time=0.5, n=3) # 3 fast beeps

    def set_state_safe(self):
        """Sets the system back to normal (Green LED on, Red/Buzzer off)."""
        if self.green_led:
            self.red_led.off()
            self.buzzer.off()
            self.green_led.on()

# Mini-test for MEMBER 2
if __name__ == "__main__":
    print("Testing actuators...")
    ac = ActuatorManager()
    ac.trigger_alarm()
    time.sleep(3)
    ac.set_state_safe()
    print("Test complete.")

