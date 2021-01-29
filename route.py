from util import find_directions, decode, get_accidents
from geo import contains_location, is_location_on_edge
from typing import Tuple, List


LatLng = Tuple[float, float]


def best_path_contains(origin: LatLng, destination: LatLng, method: str, accidents: List[dict]) -> dict:
    weighted_routes = []
    routes = find_directions(origin, destination, method)
    if routes[0] == 'error':
        print(routes[1])
        return {'route': 'No Routes Found', 'points': [], 'weight': 0}
    for route in routes:
        weight = 0

        # Extracting necessary details of route object
        encoded_polyline = route['overview_polyline']['points'] # encoded polyline of route
        distance = route["legs"][0]["distance"]["value"]  # distance is calculated in meters
        steps = route['legs'][0]['steps'] # all steps needed to reach destination
        warnings = route['warnings']
        decoded_poly = decode(encoded_polyline)
        mid_point = decoded_poly[int(len(decoded_poly) / 2)]
        radius = distance * (3 / 2)  # radius is the radius of the circle that encompasses the polyline in meters

        near_accidents = get_accidents(mid_point[1], mid_point[0], radius, accidents)

        polyline = decoded_poly
        for accident in near_accidents:
            if contains_location(accident, polyline, True):
                weight += accident['total_weight']

        weighted_routes.append(
            {'route': decoded_poly, 'points': encoded_polyline, 'steps': steps, 'warnings': warnings, 'weight': weight, 'algorithm': 'contains_location'})

    least_weighted_route = weighted_routes[0]
    max_weight = weighted_routes[0]['weight']
    n = 1
    print(f'--------------------------')
    for weighted_route in weighted_routes:
        c_weight = weighted_route['weight']
        print(f'Route #{n}: weight of {c_weight}')
        n += 1
        if c_weight < max_weight:
            max_weight = c_weight
            least_weighted_route = weighted_route

    return least_weighted_route


def best_path_edge(origin: LatLng, destination: LatLng, method: str, accidents: List[dict], tolerance) -> dict:
    weighted_routes = []
    routes = find_directions(origin, destination, method)
    if routes[0] == 'error':
        print(routes[1])
        return {'route': 'No Routes Found', 'points': [], 'weight': 0}
    for route in routes:
        weight = 0

        # Extracting necessary details of route object
        encoded_polyline = route['overview_polyline']['points']  # encoded polyline of route
        distance = route["legs"][0]["distance"]["value"]  # distance is calculated in meters
        steps = route['legs'][0]['steps']  # all steps needed to reach destination
        warnings = route['warnings']
        decoded_poly = decode(encoded_polyline)
        mid_point = decoded_poly[int(len(decoded_poly) / 2)]
        radius = distance * (3 / 2)  # radius is the radius of the circle that encompasses the polyline in meters

        near_accidents = get_accidents(mid_point[1], mid_point[0], radius, accidents)

        polyline = decoded_poly
        for accident in near_accidents:
            if is_location_on_edge(accident, polyline, True, tolerance):
                weight += accident['total_weight']

        weighted_routes.append(
            {'route': decoded_poly, 'points': encoded_polyline, 'steps': steps, 'warnings': warnings, 'weight': weight, 'algorithm': 'location_edge', 'tolerance': tolerance})

    least_weighted_route = weighted_routes[0]
    max_weight = weighted_routes[0]['weight']
    n = 1
    print(f'--------------------------')
    for weighted_route in weighted_routes:
        c_weight = weighted_route['weight']
        print(f'Route #{n}: weight of {c_weight}')
        n += 1
        if c_weight < max_weight:
            max_weight = c_weight
            least_weighted_route = weighted_route

    return least_weighted_route
