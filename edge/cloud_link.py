import json
import time

class CloudLink:
    def __init__(self, client_id="EdgePi-01", topic="edge-ai/telemetry"):
        """
        Connects to AWS IoT Core.
        MEMBER 3: Provide the certificates and AWS Endpoint!
        MEMBER 4: Integrate AWSIoTMQTTClient here.
        """
        self.topic = topic
        self.client_id = client_id
        self.connected = False
        
        print("CloudLink initialized. (Pending AWS Connection)")
        # TODO: AWSIoTMQTTClient setup and connect()
        
    def publish_telemetry(self, data):
        """Publishes a JSON payload to the AWS topic."""
        if not self.connected:
            # print("Warning: AWS not connected. Payload dropped.")
            return

        payload = json.dumps(data)
        # TODO: self.client.publish(self.topic, payload, 1)
        print(f"Published to AWS: {payload}")
