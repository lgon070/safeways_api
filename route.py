from util import find_directions, decode, get_accidents, within_bounds_center
from geo import contains_location, is_location_on_edge
from typing import Tuple, List

LatLng = Tuple[float, float]


def best_path_contains(origin: LatLng, destination: LatLng, method: str, accidents: List[dict]) -> dict:
    within_bounds = within_bounds_center(origin, destination)
    weighted_routes = []
    accidents_in_route = []
    fd_response = find_directions(origin, destination, method)
    if fd_response['status'] == 'OK':
        for route in fd_response['routes']:
            weight = 0
            # Extracting necessary details of route object
            encoded_polyline = route['overview_polyline']['points']  # encoded polyline of route
            distance = route["legs"][0]["distance"]["value"]  # distance is calculated in meters
            steps = route['legs'][0]['steps']  # all steps exineeded to reach destination
            warnings = route['warnings']
            decoded_poly = decode(encoded_polyline)
            mid_point = decoded_poly[int(len(decoded_poly) / 2)]
            radius = distance * (3 / 2)  # radius is the radius of the circle that encompasses the polyline in meters

            near_accidents = get_accidents(mid_point[1], mid_point[0], radius, accidents)

            polyline = decoded_poly
            for accident in near_accidents:
                if contains_location(accident, polyline, True):
                    weight += accident['accident_weight']
                    accidents_in_route.append({'accident_id': accident['accident_id'], 'accident_weight': accident['accident_weight']})

            weighted_route = {'route': decoded_poly, 'points': encoded_polyline, 'steps': steps, 'warnings': warnings,
                              'weight': weight, 'accidents_in_route': accidents_in_route}
            if weight == 0:
                if len(near_accidents) == 0:
                    weighted_route['accurate_zero_weight'] = False
                else:
                    weighted_route['accurate_zero_weight'] = True
            weighted_routes.append(weighted_route)

        # bubble sort weighted routes
        n = len(weighted_routes)
        for i in range(n):
            for j in range(0, n - i - 1):
                if weighted_routes[j]['weight'] > weighted_routes[j + 1]['weight']:
                    weighted_routes[j], weighted_routes[j + 1] = weighted_routes[j + 1], weighted_routes[j]

        return {'status': fd_response['status'], 'weighted_routes': weighted_routes, 'within_la_bounds': within_bounds,
                'algorithm': 'contains_location'}
    else:
        print(fd_response['log_error_google'])
        return {'status': fd_response['status'], 'error_message': fd_response['user_error_msg'], 'weighted_routes': []}


def best_path_edge(origin: LatLng, destination: LatLng, method: str, accidents: List[dict], tolerance) -> dict:
    within_bounds = within_bounds_center(origin, destination)
    weighted_routes = []
    accidents_in_route = []
    fd_response = find_directions(origin, destination, method)
    if fd_response['status'] == 'OK':
        for route in fd_response['routes']:
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
                    weight += accident['accident_weight']
                    accidents_in_route.append({'accident_id': accident['accident_id'], 'accident_weight': accident['accident_weight']})

            weighted_route = {'route': decoded_poly, 'points': encoded_polyline, 'steps': steps, 'warnings': warnings,
                              'weight': weight, 'accidents_in_route': accidents_in_route}
            if weight == 0:
                if len(near_accidents) == 0:
                    weighted_route['accurate_zero_weight'] = False
                else:
                    weighted_route['accurate_zero_weight'] = True
            weighted_routes.append(weighted_route)

        # bubble sort weighted routes
        n = len(weighted_routes)
        for i in range(n):
            for j in range(0, n - i - 1):
                if weighted_routes[j]['weight'] > weighted_routes[j + 1]['weight']:
                    weighted_routes[j], weighted_routes[j + 1] = weighted_routes[j + 1], weighted_routes[j]

        return {'status': fd_response['status'], 'weighted_routes': weighted_routes, 'within_la_bounds': within_bounds,
                'algorithm': 'location_edge',
                'tolerance': tolerance}
    else:
        print(fd_response['log_error_google'])
        return {'status': fd_response['status'], 'error_message': fd_response['user_error_msg'], 'weighted_routes': []}
