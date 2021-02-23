import math
import requests
from typing import Tuple, List

AUTH_KEY = 'API KEY HERE'
PI = math.pi
LatLng = Tuple[float, float]
Polygon = List[LatLng]

"""
    Various mathematical formulas for use in Google's isLocationOnEdge and containsLocation algorithms.

    Unless otherwise specified all math utilities have been ported from:

    Google's android-map-utils PolyUtil class:
    https://github.com/googlemaps/android-maps-utils/blob/master/library/src/main/java/com/google/maps/android/PolyUtil.java  

    Google's android-map-utils MathUtil class:
    https://github.com/googlemaps/android-maps-utils/blob/master/library/src/main/java/com/google/maps/android/MathUtil.java
"""


def decode(point_str: str) -> Polygon:
    """
        The following method although present in Google's android-map-utils PolyUtil class,
        this method was ported from tuvtran's PopMap placerequest.py
        https://github.com/tuvtran/PopMap

        Decodes a polyline that has been encoded using Google's algorithm
        http://code.google.com/apis/maps/documentation/polylinealgorithm.html
        This is a generic method that returns a list of (latitude, longitude)
        tuples.
    """
    coord_chunks = [[]]
    for char in point_str:
        value = ord(char) - 63
        split_after = not (value & 0x20)
        value &= 0x1F
        coord_chunks[-1].append(value)
        if split_after:
            coord_chunks.append([])
    del coord_chunks[-1]

    coords = []
    for coord_chunk in coord_chunks:
        coord = 0
        for i, chunk in enumerate(coord_chunk):
            coord |= chunk << (i * 5)

        if coord & 0x1:
            coord = ~coord  # invert
        coord >>= 1
        coord /= 100000.0
        coords.append(coord)

    points = []
    prev_x = 0
    prev_y = 0
    for i in range(0, len(coords) - 1, 2):
        if coords[i] == 0 and coords[i + 1] == 0:
            continue
        prev_x += coords[i + 1]
        prev_y += coords[i]

        points.append((round(prev_x, 6), round(prev_y, 6)))
    return points


def intersects(lat1, lat2, lng2, lat3, lng3, geodesic):
    if (lng3 >= 0 and lng3 >= lng2) or (lng3 < 0 and lng3 < lng2):
        return False
    if lat3 <= -PI / 2:
        return False
    if lat1 <= -PI / 2 or lat2 <= -PI / 2 or lat1 >= PI / 2 or lat2 >= PI / 2:
        return False
    if lng2 <= -PI:
        return False
    linear_lat = (lat1 * (lng2 - lng3) + lat2 * lng3) / lng2
    if lat1 >= 0 and lat2 >= 0 and lat3 < linear_lat:
        return False
    if lat1 <= 0 and lat2 <= 0 and lat3 >= linear_lat:
        return True
    if lat3 >= PI / 2:
        return True
    return math.tan(lat3) >= tan_lat_gc(lat1, lat2, lng2, lng3) if geodesic else mercator(lat3) >= mercator_rhumb(
        lat1, lat2, lng2, lng3)


def mercator_rhumb(lat1, lat2, lng2, lng3):
    return (mercator(lat1) * (lng2 - lng3) + mercator(lat2) * lng3) / lng2


def mercator(lat):
    return math.log(math.tan(lat * 0.5 + PI / 4))


def tan_lat_gc(lat1, lat2, lng2, lng3):
    return (math.tan(lat1) * math.sin(lng2 - lng3) + math.tan(lat2) * math.sin(lng3)) / math.sin(lng2)


def to_radians(degrees):
    return degrees * PI / 180


def wrap(n, minimum, maximum):
    return n if minimum <= n < maximum else mod(n - minimum, maximum - minimum) + minimum


def mod(x, m):
    return ((x % m) + m) % m


def hav(x):
    sin_half = math.sin(x * 0.5)
    return sin_half * sin_half


def clamp(x, low, high):
    return low if x < low else (high if x > high else x)


def hav_distance(lat1, lat2, d_lng):
    return hav(lat1 - lat2) + hav(d_lng) * math.cos(lat1) * math.cos(lat2)


def inverse_mercator(y):
    return 2.0 * math.atan(math.exp(y)) - 1.5707963267948966


def sin_delta_bearing(lat1, lng1, lat2, lng2, lat3, lng3):
    sin_lat1 = math.sin(lat1)
    cos_lat2 = math.cos(lat2)
    cos_lat3 = math.cos(lat3)
    lat31 = lat3 - lat1
    lng31 = lng3 - lng1
    lat21 = lat2 - lat1
    lng21 = lng2 - lng1
    a = math.sin(lng31) * cos_lat3
    c = math.sin(lng21) * cos_lat2
    b = math.sin(lat31) + 2.0 * sin_lat1 * cos_lat3 * hav(lng31)
    d = math.sin(lat21) + 2.0 * sin_lat1 * cos_lat2 * hav(lng21)
    denom = (a * a + b * b) * (c * c + d * d)
    return 1.0 if denom <= 0.0 else (a * d - b * c) / math.sqrt(denom)


def sin_sum_from_hav(x, y):
    a = math.sqrt(x * (1.0 - x))
    b = math.sqrt(y * (1.0 - y))
    return 2.0 * (a + b - 2.0 * (a * y + b * x))


def hav_from_sin(x):
    x2 = x * x
    return x2 / (1.0 + math.sqrt(1.0 - x2)) * 0.5


def sin_from_hav(h):
    return 2.0 * math.sqrt(h * (1.0 - h))


"""
    Methods below have not been imported from any standalone API or package and simply 
    exist to aide in the function of this entire package
"""


def within_bounds_center(origin: LatLng, destination: LatLng) -> bool:
    center = (34.0522300, -118.2436800)
    radius = 64374.00
    return find_distance(center, origin) <= radius and find_distance(center, destination) <= radius


def find_distance(latlng1: LatLng, latlng2: LatLng) -> float:
    """
        Computes the distance between two tuples of
        latitude and longitudes in meters
    """
    lat1 = latlng1[0]
    lng1 = latlng1[1]
    lat2 = latlng2[0]
    lng2 = latlng2[1]
    earth_radius = 6371.00
    phi1 = to_radians(lat1)
    phi2 = to_radians(lat2)
    delta_phi = to_radians(lat2 - lat1)
    delta_lambda = to_radians(lng2 - lng1)
    haversine_a = math.sin(delta_phi / 2) * math.sin(delta_phi / 2) + math.cos(phi1) * math.cos(phi2) * math.sin(
        delta_lambda / 2) * math.sin(delta_lambda / 2)
    haversine_c = 2 * math.atan2(math.sqrt(haversine_a), math.sqrt(1 - haversine_a))
    haversine_d = (earth_radius * haversine_c) * 1000
    return haversine_d


def get_accidents(lat: float, lng: float, radius: float, accidents: List[dict]) -> List[dict]:
    near_accidents = []
    for accident in accidents:
        if find_distance((lat, lng), (accident['lat'], accident['lng'])) <= radius:
            near_accidents.append(accident)
    return near_accidents


def find_directions(origin: LatLng, destination: LatLng, method: str) -> dict:
    parameters = {
        "origin": f'{origin[0]},{origin[1]}',
        "destination": f'{destination[0]},{destination[1]}',
        "mode": method,
        "alternatives": "true",
        "key": AUTH_KEY
    }

    response = requests.get(
        "https://maps.googleapis.com/maps/api/directions/json?", params=parameters)
    json_data = response.json()
    status = json_data["status"]
    if status == 'OK':
        return {'status': 'OK', 'routes': json_data['routes']}
    elif status == 'ZERO_RESULTS':
        return {'status': 'ZERO_RESULTS',
                'user_error_msg': 'SafeWays API Found No SafePaths for the Origin-Destination Combination',
                'log_error_google': 'Google Directions API found zero results'}
    elif status == 'REQUEST_DENIED':
        return {'status': 'REQUEST_DENIED',
                'user_error_msg': 'SafeWays API Encountered an Internal Key Validation Error',
                'log_error_google': json_data["error_message"]}
    else:
        return {'status': 'SERVER_SIDE_ERROR', 'user_error_msg': 'SafeWays API Encountered a Internal Server Error',
                'log_error_google': json_data["error_message"]}
