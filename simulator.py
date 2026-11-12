import asyncio
import random
from datetime import datetime, timezone, timedelta

MAX_OFFSET = timedelta(hours=1)


class Simulator:
    def __init__(self, routes):
        self.pending = {r["id"]: r for r in routes}
        self.busy_vehicles = set()
        self.start_times = {}

    def _actual_start(self, route):
        if route["id"] not in self.start_times:
            scheduled = datetime.fromisoformat(route["scheduled_time"])
            offset = random.triangular(-MAX_OFFSET.total_seconds(),
                                    MAX_OFFSET.total_seconds(),
                                    0)
            self.start_times[route["id"]] = scheduled + timedelta(seconds=offset)
        return self.start_times[route["id"]]

    async def run(self):
        while True:
            now = datetime.now(timezone.utc)
            for route in list(self.pending.values()):
                if (self._actual_start(route) <= now
                        and route["vehicle_id"] not in self.busy_vehicles):
                    self.pending.pop(route["id"])
                    self.busy_vehicles.add(route["vehicleId"]) # verify if I should put busy device 
                    asyncio.create_task(self.run_route(route))

            await asyncio.sleep(10)

    async def run_route(self, route):
        # todo
        raise NotImplementedError
