import json
import logging
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

class CloudLink:
    def __init__(self, client_id="EdgePi-01", topic="edge-ai/telemetry"):
        self.topic = topic
        self.client_id = client_id
        self.connected = False
        
        # --- UPDATE THESE WITH YOUR AWS DETAILS ---
        ENDPOINT = "a1cwlyvzluprga-ats.iot.eu-north-1.amazonaws.com"
        PATH_TO_CERTS = "../certs/" 
        ROOT_CA = PATH_TO_CERTS + "AmazonRootCA1.pem"
        PRIVATE_KEY = PATH_TO_CERTS + "device.key"
        CERTIFICATE = PATH_TO_CERTS + "device.crt"
        # ------------------------------------------

        print(f"Connecting to AWS IoT Core at {ENDPOINT}...")
        
        # Init AWSIoTMQTTClient
        self.client = AWSIoTMQTTClient(self.client_id)
        self.client.configureEndpoint(ENDPOINT, 8883)
        self.client.configureCredentials(ROOT_CA, PRIVATE_KEY, CERTIFICATE)
        
        # AWSIoTMQTTClient connection configuration
        self.client.configureAutoReconnectBackoffTime(1, 32, 20)
        self.client.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
        self.client.configureDrainingFrequency(2)  # Draining: 2 Hz
        self.client.configureConnectDisconnectTimeout(10)
        self.client.configureMQTTOperationTimeout(5)

        try:
            self.client.connect()
            self.connected = True
            print("✅ Successfully connected to AWS IoT Core")
        except Exception as e:
            print(f"❌ Failed to connect to AWS IoT Core: {e}")

    def publish_telemetry(self, data):
        """Publishes a JSON payload to the AWS topic."""
        if not self.connected:
            return

        try:
            payload = json.dumps(data)
            self.client.publish(self.topic, payload, 1)
            print(f"🚀 Published to {self.topic}: {payload}")
        except Exception as e:
            print(f"⚠️ Failed to publish message: {e}")
