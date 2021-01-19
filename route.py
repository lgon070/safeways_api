from geo import *
from util import *


def best_path_contains(origin: tuple(float, float), destination: tuple(float, float), method: str, accidents: list) -> dict:
    weighted_routes = []
    routes = find_directions(origin, destination, method)
    if routes[0] == "No Path Found":
        print('No Routes Found')
        return {'route': 'No Routes Found', 'points': [], 'weight': 0}
    for route in routes:
        weight = 0
        distance = route["legs"][0]["distance"]["value"]  # distance is calculated in meters
        decoded_poly = decode(route["overview_polyline"]["points"])
        mid_point = decoded_poly[int(len(decoded_poly) / 2)]
        radius = distance * (3 / 2)  # radius is the radius of the circle that encompasses the polyline in meters

        near_accidents = get_accidents(mid_point[1], mid_point[0], radius, accidents)

        polyline = decoded_poly
        for accident in near_accidents:
            if contains_location(accident, polyline, True):
                weight += accident['severity']

        weighted_routes.append({'route': decoded_poly, 'points': route["overview_polyline"]["points"], 'weight': weight})

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


def best_path_edge(origin: tuple(float, float), destination: tuple(float, float), method: str, accidents: list) -> dict:
    weighted_routes = []
    routes = find_directions(origin, destination, method)
    if routes[0] == "No Path Found":
        print('No Routes Found')
        return {'route': 'No Routes Found', 'points': [], 'weight': 0}
    for route in routes:
        weight = 0
        distance = route["legs"][0]["distance"]["value"]  # distance is calculated in meters
        decoded_poly = decode(route["overview_polyline"]["points"])
        mid_point = decoded_poly[int(len(decoded_poly) / 2)]
        radius = distance * (3 / 2)  # radius is the radius of the circle that encompasses the polyline in meters

        near_accidents = get_accidents(mid_point[1], mid_point[0], radius, accidents)

        polyline = decoded_poly
        for accident in near_accidents:
            if is_location_on_edge(accident, polyline, True, 25):
                weight += accident['severity']

        weighted_routes.append({'route': decoded_poly, 'points': route["overview_polyline"]["points"], 'weight': weight})

    print(weighted_routes)

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
