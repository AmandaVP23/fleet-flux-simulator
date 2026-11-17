import asyncio
import random
import polyline
import json
from driver import calculate_target_speed, get_driver_factor, step_speed
from route_math import get_accumulated_distance, get_route_average_speed, locate, position_at
from datetime import datetime, timezone, timedelta
from backend_client import get_route_details, load_devices, get_route_summary
from config import TICK_SECONDS
from profiles import get_profile
from device import SimulatedDevice
import paho.mqtt.client as mqtt

from config import MQTT_HOST, MQTT_PORT


MAX_OFFSET = timedelta(hours=1)


class Simulator:
    def __init__(self, routes, devices):
        # the device is the actor: routes only carry the vehicle, so go vehicle -> device
        self.device_by_vehicle = { d["vehicle"]["id"]: d for d in devices }
        self.sim_devices = { d["deviceId"]: SimulatedDevice.from_api(d) for d in devices }
        self.pending = {}
        for r in routes:
            if r["vehicle"]["id"] in self.device_by_vehicle:
                self.pending[r["id"]] = r
            else:
                print(f"skipping route {r['id']}: vehicle {r['vehicle']['id']} has no device")
        self.busy_devices = set()
        self.start_times = {}


    def _actual_start(self, route):
        if route["id"] not in self.start_times:
            scheduled = datetime.fromisoformat(route["scheduledTime"])
            offset = random.triangular(-MAX_OFFSET.total_seconds(),
                                    MAX_OFFSET.total_seconds(),
                                    0)
            self.start_times[route["id"]] = scheduled + timedelta(seconds=offset)
        return self.start_times[route["id"]]


    def start(self):
        for d in self.sim_devices.values():
            d.connect()


    def stop(self):
        for d in self.sim_devices.values():
            d.disconnect()


    async def run(self):
        self.loop = asyncio.get_running_loop()
        self._start_listener()
        while True:
            now = datetime.now(timezone.utc)
            for route in list(self.pending.values()):
                device = self.device_by_vehicle[route["vehicle"]["id"]]
                print("trying to run")
                if (self._actual_start(route) <= now and device["deviceId"] not in self.busy_devices):
                    self.pending.pop(route["id"])
                    self.busy_devices.add(device["deviceId"])
                    asyncio.create_task(self._run_and_release(route, device))

            await asyncio.sleep(10)


    def _start_listener(self):
        mqttClient = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="simulator-control")
        mqttClient.on_connect = lambda client, *_: client.subscribe("fleet/config/#", qos=1)
        mqttClient.on_message = self._on_message
        mqttClient.connect(MQTT_HOST, MQTT_PORT)
        mqttClient.loop_start()
        self.control = mqttClient
        
    
    def _on_message(self, client, userdata, msg):
        # paho thread -> hand over to the asyncio loop
        asyncio.run_coroutine_threadsafe(self._handle(msg.topic, json.loads(msg.payload)), self.loop)


    async def _handle(self, topic, event):
        if topic.endsWith("/devices"):
            devices = await asyncio.to_thread(load_devices)
            self.device_by_vehicle = { d["vehicle"]["id"]: d for d in devices }
            for d in devices:
                if d["deviceId"] not in self.sim_devices:
                    sd = self.sim_devices[d["deviceId"]] = SimulatedDevice.from_api(d)
                    sd.connect()
        elif topic.endWith("/routes"):
            route = await asyncio.to_thread(get_route_summary, event["id"])
            if route and route["vehicle"]["id"] in self.device_by_vehicle:
                self.pending[route["id"]] = route


    async def _run_and_release(self, route, device):
        """Runs the route and frees the device"""
        print("inside run_and_release")
        try:
            await self.run_route(route, device)
        finally:
            self.busy_devices.discard(device["deviceId"])
            

    async def run_route(self, route, device):
        route_details = get_route_details(route["id"])

        if route_details == None:
            return

        profile = get_profile(route["vehicle"]["type"])
        driver_factor = get_driver_factor(device["driverId"])
        distance_meters = route_details["segmentDistancesInMeters"]
        duration_seconds = route_details["segmentDurationsInSeconds"]
    
        coordinates = polyline.decode(route_details["geometry"], route_details["geometryPrecision"], geojson=True)  # (lon, lat)
        accumulated_distance = get_accumulated_distance(distance_meters);

        route_average_speed = get_route_average_speed(route["distanceMeters"], route["durationSeconds"])
        meters = 0
        current_speed = route_average_speed / 2;
        target_speed = 0;
        locate_result = locate(accumulated_distance, meters, 0)
        current_position_index = locate_result[0]

        while True:
            duration = duration_seconds[current_position_index]
            if duration > 0:
                speed_seg = distance_meters[current_position_index] / duration
            else:
                speed_seg = route_average_speed

            # 1. speed: aim for the current segment's speed, limited by the vehicle's acceleration/braking
            speed_seg = distance_meters[current_position_index] / duration_seconds[current_position_index]
            target_speed = calculate_target_speed(speed_seg, driver_factor, profile["max_speed"])
            current_speed = step_speed(current_speed, target_speed,
                                       profile["max_acceleration"], profile["max_deceleration"],
                                       TICK_SECONDS)

            # 2. position: advance by the speed we actually reached
            meters += current_speed * TICK_SECONDS
            locate_result = locate(accumulated_distance, meters, current_position_index)

            if locate_result is None:
                # todo finish and send destination point
                return

            current_position_index = locate_result[0]
            long, lat = position_at(coordinates, distance_meters, current_position_index, locate_result[1])
            self.sim_devices[device["deviceId"]].publish_position(lat=lat, lon=long, speed=current_speed)


            await asyncio.sleep(TICK_SECONDS)


