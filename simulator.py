import asyncio
import random
import polyline
from driver import calculate_target_speed, get_driver_factor, step_speed
from route_math import get_accumulated_distance, get_route_average_speed, locate, position_at
from datetime import datetime, timezone, timedelta
from backend_client import get_route_details
from config import TICK_SECONDS
from profiles import get_profile

MAX_OFFSET = timedelta(hours=1)


class Simulator:
    def __init__(self, routes, devices):
        # the device is the actor: routes only carry the vehicle, so go vehicle -> device
        self.device_by_vehicle = {d["vehicle"]["id"]: d for d in devices}
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

    async def run(self):
        while True:
            now = datetime.now(timezone.utc)
            for route in list(self.pending.values()):
                device = self.device_by_vehicle[route["vehicle"]["id"]]
                if (self._actual_start(route) <= now and device["deviceId"] not in self.busy_devices):
                    self.pending.pop(route["id"])
                    self.busy_devices.add(device["deviceId"])
                    asyncio.create_task(self._run_and_release(route, device))

            await asyncio.sleep(10)

    async def _run_and_release(self, route, device):
        """Runs the route and always frees the device, even on early return or error."""
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

        meters = 0;
        # todo protect
        current_speed = get_route_average_speed(route["distanceMeters"], route["durationSeconds"]) / 2;
        target_speed = 0;
        locate_result = locate(accumulated_distance, meters, 0)
        current_position_index = locate_result[0]

        while True:
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
                return

            current_position_index = locate_result[0]
            long, lat = position_at(coordinates, distance_meters, current_position_index, locate_result[1])

            await asyncio.sleep(TICK_SECONDS)
