import asyncio

from backend_client import load_devices, load_initial_routes
from simulator import Simulator


def main():
    print("Hello from fleet-flux-simulator!")

    devices = load_devices();
    # routes = load_initial_routes();

    print(devices)

    # simulator = Simulator(routes, devices)
    # asyncio.run(simulator.run())

    # route = result["routes"][0]
    # distance = route["legs"][0]["annotation"]["distance"]
    # speed = route["legs"][0]["annotation"]["speed"]
    # coordinates = route["geometry"]["coordinates"]

    # accumulated_distance = get_accumulated_distance(distance);

    # meters = 0;
    # start_index = 0;
    # current_speed = speed[0] / 2; 
    # target_speed = 0;
    # max_speed_change_per_tick = 2; # m/s
    # locate_result = locate(accumulated_distance, meters, 0)

    # for i in range(0, 10): 
    #     speed_seg = speed[locate_result[0]]
    #     variated_speed = speed_seg * random.uniform(0.75, 1.3) # m/s
                
    #     meters += (variated_speed * 5)
    #     locate_result = locate(accumulated_distance, meters, locate_result[0])
    #     if (locate_result == None):
    #         print("route ended")
    #         return

    #     start_index = locate_result[0]
    #     distance_seg_value = distance[locate_result[0]]
    #     offset = locate_result[1] / distance_seg_value
    #     coordinates_seg = coordinates[locate_result[0]]
    #     coordinates_seg_next = coordinates[locate_result[0] + 1]
    #     delta_long = coordinates_seg_next[0] - coordinates_seg[0]
    #     delta_lat = coordinates_seg_next[1] - coordinates_seg[1]
    #     long = coordinates_seg[0] + (delta_long * offset)
    #     lat = coordinates_seg[1] + (delta_lat * offset)
    #     # speed_seg = speed[locate_result[0]]
    #     target_speed = calculate_target_spec(speed_seg, 1)

    #     print("speed_seg", speed_seg, "current", current_speed, target_speed)

    #     # this value will be by vehicle
    #     max_acceleration = 1.5 # m/s
    #     max_deceleration = random.triangular(1.5, 3.5, 2)
    #     if current_speed < target_speed:
    #         current_speed = min(current_speed + max_acceleration * 5, target_speed) # * tick
    #     elif current_speed > target_speed:
    #         current_speed = max(current_speed - max_deceleration * 5, target_speed)

    #     print("current", current_speed)
    



if __name__ == "__main__":
    main()


