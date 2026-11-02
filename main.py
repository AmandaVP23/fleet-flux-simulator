import osrm
import random

def locate(accumulated, total_meters, start_index):
    for i in range(start_index, len(accumulated)):
        value = accumulated[i]
        if value > total_meters:
            start = 0
            if (i > 0):
                start = accumulated[i - 1]; 

            return (i, total_meters - start);
    return None;


def get_accumulated_distance(distance):
    total = 0
    accumulated = []
    for i in range(len(distance)):
        total += distance[i]
        accumulated.append(total)

    return accumulated;


def calculate_target_spec(seg_max_speed, driver_factor):
    """
    seg_max_speed - OSRM speed in m/s
    returns the goal speed in m/s
    """
    variation = random.uniform(0.95, 1.05)

    factor = driver_factor * variation

    factor = min(factor, 1.125)

    return seg_max_speed * factor



def main():
    print("Hello from fleet-flux-simulator!")

    engine = osrm.OSRM(
        storage_config="osrm-data/iberia.osrm",
        algorithm="MLD",
        use_shared_memory=False,
    )

    params = osrm.RouteParameters(
        coordinates=[
            (-8.818650998366033, 39.75819789378323),
            (-8.823567153717807, 39.734349229055624),
            # (-8.927016561382153, 39.33275841892133)
        ],
        # alternatives=2,
        overview="git rev-list --objects HEAD | git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' | sort -k3 -n | tail -20",
        geometries="geojson",
        steps=True,
        # number_of_alternatives=3,
        annotations=["speed", "distance", "duration"],
    )

    result = engine.Route(params)

    route = result["routes"][0]
    distance = route["legs"][0]["annotation"]["distance"]
    speed = route["legs"][0]["annotation"]["speed"]
    coordinates = route["geometry"]["coordinates"]

    accumulated_distance = get_accumulated_distance(distance);

    meters = 0;
    start_index = 0;
    current_speed = speed[0] / 2; 
    target_speed = 0;
    max_speed_change_per_tick = 2; # m/s
    locate_result = locate(accumulated_distance, meters, 0)

    for i in range(0, 10): 
        speed_seg = speed[locate_result[0]]
        variated_speed = speed_seg * random.uniform(0.75, 1.3) # m/s
                
        meters += (variated_speed * 5)
        locate_result = locate(accumulated_distance, meters, locate_result[0])
        if (locate_result == None):
            print("route ended")
            return

        start_index = locate_result[0]
        distance_seg_value = distance[locate_result[0]]
        offset = locate_result[1] / distance_seg_value
        coordinates_seg = coordinates[locate_result[0]]
        coordinates_seg_next = coordinates[locate_result[0] + 1]
        delta_long = coordinates_seg_next[0] - coordinates_seg[0]
        delta_lat = coordinates_seg_next[1] - coordinates_seg[1]
        long = coordinates_seg[0] + (delta_long * offset)
        lat = coordinates_seg[1] + (delta_lat * offset)
        # speed_seg = speed[locate_result[0]]
        target_speed = calculate_target_spec(speed_seg, 1)

        print("speed_seg", speed_seg, "current", current_speed, target_speed)

        # this value will be by vehicle
        max_acceleration = 1.5 # m/s
        max_deceleration = random.triangular(1.5, 3.5, 2)
        if current_speed < target_speed:
            current_speed = min(current_speed + max_acceleration * 5, target_speed) # * tick
        elif current_speed > target_speed:
            current_speed = max(current_speed - max_deceleration * 5, target_speed)

        print("current", current_speed)
    

    



if __name__ == "__main__":
    main()


