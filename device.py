import json
from datetime import datetime, timezone

import paho.mqtt.client as mqtt

from config import MQTT_HOST, MQTT_PORT, MQTT_TOPIC_TEMPLATE


class SimulatedDevice:
    """One tracker device = one MQTT connection (client_id == deviceId)."""

    def __init__(self, device_id, vehicle_id, driver_id=None):
        self.device_id = device_id
        self.vehicle_id = vehicle_id
        self.driver_id = driver_id
        self.topic = MQTT_TOPIC_TEMPLATE.format(device_id=device_id)
        # paho needs client_id to be a str, the API returns a long
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=str(device_id))

    @classmethod
    def from_api(cls, data):
        """Build from one item of GET /simulator/devices."""
        return cls(data["deviceId"], data["vehicle"]["id"], data.get("driverId"))

    def connect(self):
        self.client.connect(MQTT_HOST, MQTT_PORT)
        self.client.loop_start()

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()

    def publish_position(self, lat, lon, speed):
        payload = {
            "vehicleId": self.vehicle_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "lat": lat,
            "lon": lon,
            "speed": speed,
        }
        self.client.publish(self.topic, json.dumps(payload), qos=1)
