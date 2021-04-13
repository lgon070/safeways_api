import math
import requests
from typing import Tuple, List

AUTH_KEY = 'GOOGLE API KEY'
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


def within_city_bounds(origin: LatLng, destination: LatLng) -> bool:
    la_bounds = [(33.8641899712294, -118.281468637671), (33.8627792, -118.2814372),
                 (33.862734758137, -118.281534783721),
                 (33.8415, -118.2825), (33.8415, -118.2965), (33.8135, -118.293), (33.803, -118.2965),
                 (33.803, -118.2685), (33.81, -118.265), (33.81, -118.2545), (33.803, -118.251), (33.7995, -118.23),
                 (33.81, -118.2265), (33.824, -118.2335), (33.8345, -118.23), (33.8345, -118.223), (33.824, -118.2195),
                 (33.789, -118.223), (33.7855, -118.216), (33.7785, -118.216), (33.7645, -118.2405), (33.754, -118.237),
                 (33.754, -118.244), (33.7155, -118.2265), (33.6875, -118.223), (33.6875, -118.237), (33.67, -118.251),
                 (33.6595, -118.272), (33.656, -118.321), (33.6595, -118.349), (33.67, -118.3665), (33.7295, -118.335),
                 (33.733, -118.3245), (33.7505, -118.321), (33.7505, -118.314), (33.8695, -118.314),
                 (33.873, -118.2965),
                 (33.9465, -118.2965), (33.936, -118.3035), (33.936, -118.3175), (33.9675, -118.321),
                 (33.964, -118.335),
                 (33.978, -118.3385), (33.978, -118.3665), (33.9605, -118.3665), (33.957, -118.3735),
                 (33.957, -118.3665),
                 (33.9325, -118.363), (33.9255, -118.3665), (33.929, -118.4225), (33.9115, -118.419),
                 (33.9115, -118.503),
                 (33.9535, -118.5275), (33.964, -118.5415), (33.971, -118.5415), (34.0165, -118.4505),
                 (34.0235, -118.454), (34.041, -118.475), (34.0375, -118.4855), (34.0445, -118.4925),
                 (33.9815, -118.552),
                 (33.985, -118.573), (34.041, -118.5695), (34.0655, -118.573), (34.069, -118.601), (34.076, -118.6045),
                 (34.1285, -118.5695), (34.1425, -118.608), (34.1425, -118.6325), (34.16, -118.6465),
                 (34.167, -118.664),
                 (34.174, -118.664), (34.1775, -118.671), (34.2125, -118.671), (34.216, -118.664), (34.2405, -118.65),
                 (34.2405, -118.636), (34.272, -118.636), (34.279, -118.629), (34.279, -118.5975), (34.307, -118.5905),
                 (34.3, -118.5485), (34.3105, -118.552), (34.321, -118.5485), (34.3175, -118.5345), (34.342, -118.5065),
                 (34.335, -118.4925), (34.335, -118.405), (34.3245, -118.4015), (34.321, -118.391),
                 (34.3035, -118.4015),
                 (34.3035, -118.384), (34.2895, -118.377), (34.2895, -118.3665), (34.2825, -118.3595),
                 (34.2895, -118.3035), (34.2965, -118.3035), (34.2965, -118.2825), (34.2825, -118.2825),
                 (34.286, -118.2755), (34.2825, -118.2335), (34.265, -118.2335), (34.2615, -118.251),
                 (34.251, -118.251),
                 (34.2475, -118.2615), (34.2195, -118.2615), (34.216, -118.3315), (34.202, -118.3385),
                 (34.1985, -118.3595), (34.167, -118.3525), (34.1495, -118.342), (34.16, -118.3245), (34.16, -118.314),
                 (34.167, -118.3105), (34.16, -118.2755), (34.125, -118.258), (34.1285, -118.2405), (34.139, -118.2405),
                 (34.139, -118.2335), (34.153, -118.23), (34.1495, -118.209), (34.1565, -118.195), (34.153, -118.181),
                 (34.141965071875, -118.181), (34.1418339, -118.180908), (34.1412999, -118.180757),
                 (34.1412019, -118.180646), (34.1411289, -118.180513), (34.1410909, -118.180082),
                 (34.1408809, -118.180097), (34.1408179, -118.180198), (34.1407129, -118.180766),
                 (34.1407352709369, -118.181), (34.132, -118.181), (34.1285, -118.1635), (34.118, -118.1635),
                 (34.111, -118.167), (34.111, -118.174), (34.104, -118.174), (34.104, -118.153), (34.0585, -118.16),
                 (34.0585, -118.188), (34.0095, -118.188), (34.0095, -118.237), (33.985, -118.2335), (33.985, -118.251),
                 (33.957, -118.251), (33.957, -118.23), (33.95, -118.223), (33.9255, -118.2265), (33.9255, -118.251),
                 (33.9185, -118.251), (33.9185, -118.279)]

    return inside_polygon(origin, la_bounds) and inside_polygon(destination, la_bounds)


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


def inside_polygon(point, polygon):
    n = len(polygon)
    inside = False
    x = point[0]
    y = point[1]
    p1x, p1y = polygon[0]
    for i in range(n + 1):
        x_ints = 0
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        x_ints = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= x_ints:
                        inside = not inside
        p1x, p1y = p2x, p2y

    return inside


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

    # print(f'https://maps.googleapis.com/maps/api/directions/json?origin={origin[0]},{origin[1]}&destination={destination[0]},{destination[1]}&mode={method}&alternative=true&key={AUTH_KEY}')
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
