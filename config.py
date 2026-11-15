import os
from dotenv import load_dotenv

load_dotenv()
OSRM_SERVER_URL = os.environ["OSRM_SERVER_URL"].rstrip("/")
BACKEND_URL = os.getenv("BACKEND_URL", "https://localhost:8443").rstrip("/")
TICK_SECONDS = float(os.getenv("TICK_SECONDS", "5"))
MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC_TEMPLATE = os.getenv("MQTT_TOPIC_TEMPLATE", "fleet/devices/{device_id}/telemetry")
CLIENT_CERT =("certs/simulator.crt", "certs/simulator.key")
CA_CERT = "certs/ca.crt"