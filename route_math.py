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
    """
    coordinates - list of (lon, lat) points
    distance - length in meters of each segment (coordinates[i] -> coordinates[i + 1])
    Returns (lon, lat) at offset_meters into the given segment.
    """
    ratio = offset_meters / distance[segment_index]
    lon1, lat1 = coordinates[segment_index]
    lon2, lat2 = coordinates[segment_index + 1]

    return (lon1 + (lon2 - lon1) * ratio, lat1 + (lat2 - lat1) * ratio)
