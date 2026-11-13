import asyncio
import random
import polyline
from driver import calculate_target_speed, step_speed
from route_math import get_accumulated_distance, locate
from datetime import datetime, timezone, timedelta
from backend_client import get_route_details
from config import TICK_SECONDS

MAX_OFFSET = timedelta(hours=1)


class Simulator:
    def __init__(self, routes):
        self.pending = {r["id"]: r for r in routes}
        self.busy_vehicles = set()
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
                if (self._actual_start(route) <= now and route["vehicle"]["id"] not in self.busy_vehicles):
                    self.pending.pop(route["id"])
                    self.busy_vehicles.add(route["vehicle"]["id"]) # verify if I should put busy device 
                    asyncio.create_task(self.run_route(route))

            await asyncio.sleep(10)

    async def run_route(self, route):
        # todo - this request should not raise on error, if it throws a 404 it should just log it and keep going
        route_details = get_route_details(route["id"])
        distance_meters = route_details["segmentDistancesInMeters"]
        duration_seconds = route_details["segmentDurationsInSeconds"]
    
        print()
        print()
        coordinates = polyline.decode(route_details["geometry"], route_details["geometryPrecision"]);
        accumulated_distance = get_accumulated_distance(distance_meters);

        meters = 0;
        # todo - handle duration - 0
        current_speed = (distance_meters[0] / duration_seconds[0]) / 2;
        target_speed = 0;
        max_speed_change_per_tick = 2 # m/s
        locate_result = locate(accumulated_distance, meters, 0)
        current_position_index = locate_result[0]
        print("initial currentSpeed: ", current_speed);
        print()
        run = True;

        while run == True:
            speed_seg = distance_meters[locate_result[0]] / duration_seconds[locate_result[0]]
            print("speed_seg", speed_seg)
            variated_speed = speed_seg * random.uniform(0.75, 1.3) # m/s
            print("variated_speed", variated_speed)
    
            meters += (variated_speed * TICK_SECONDS)
            locate_result = locate(accumulated_distance, meters, current_position_index)

            if locate_result == None:
                print("route ended")
                run = False
                return

            current_position_index = locate_result[0]
            distance_seg_value = distance_meters[current_position_index]
            offset = locate_result[1] / distance_seg_value
            coordinates_seg = coordinates[current_position_index]
            coordinates_seg_next = coordinates[current_position_index + 1]
            delta_long = coordinates_seg_next[0] - coordinates_seg[0]
            delta_lat = coordinates_seg_next[1] - coordinates_seg[1]
            long = coordinates_seg[0] + (delta_long * offset)
            lat = coordinates_seg[1] + (delta_lat * offset)
            # todo driver ratio 
            target_speed = calculate_target_speed(speed_seg, 1)

            print("speed_seg", speed_seg, "current", current_speed, "target", target_speed)

            max_acceleration = 1.5 # m/s
            max_deceleration = random.triangular(1.5, 3.5, 2)
            current_speed = step_speed(current_speed, target_speed, max_acceleration, max_deceleration, TICK_SECONDS)

            print("current", current_speed) 
        


        print()
        print()
        
        # todo
        # convert the geometry in polyline
        raise NotImplementedError
