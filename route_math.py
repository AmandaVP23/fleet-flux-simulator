def locate(accumulated, total_meters, start_index):
    for i in range(start_index, len(accumulated)):
        value = accumulated[i]
        if value > total_meters:
            start = 0
            if i > 0:
                start = accumulated[i - 1]

            return (i, total_meters - start)
    return None


def get_accumulated_distance(distance):
    total = 0
    accumulated = []
    for d in distance:
        total += d
        accumulated.append(total)

    return accumulated


def position_at(coordinates, distance, segment_index, offset_meters):
    """Returns (lon, lat) at offset_meters into the given segment."""
    # todo - move the interpolation from the commented block in main.py
    raise NotImplementedError
