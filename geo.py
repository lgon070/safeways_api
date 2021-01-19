from util import *

EARTH_RADIUS = 6371009.0
PI = math.pi


def contains_location(point: dict, polygon: list[tuple(float, float)], geodesic: bool) -> bool:
    """
      Computes whether the given point lies inside the specified polygon.
      The polygon is always considered closed, regardless of whether the last point equals
      the first or not.
      Inside is defined as not containing the South Pole -- the South Pole is always outside.
      The polygon is formed of great circle segments if geodesic is true, and of rhumb
      (loxodromic) segments otherwise.

      Ported from Google's android-map-utils PolyUtil class:
      https://github.com/googlemaps/android-maps-utils/blob/master/library/src/main/java/com/google/maps/android/PolyUtil.java
    """
    size = len(polygon)
    if size == 0:
        return False
    lat3 = to_radians(point['lat'])
    lng3 = to_radians(point['lng'])
    prev = polygon[size - 1]
    lat1 = to_radians(prev[1])
    lng1 = to_radians(prev[0])
    n_intersect = 0
    for point2 in polygon:
        d_lng3 = wrap(lng3 - lng1, -PI, PI)
        if lat3 == lat1 and d_lng3 == 0:
            return True
        lat2 = to_radians(point2[1])
        lng2 = to_radians(point2[0])
        if intersects(lat1, lat2, wrap(lng2 - lng1, -PI, PI), lat3, d_lng3, geodesic):
            n_intersect += 1
        lat1 = lat2
        lng1 = lng2
    return (n_intersect & 1) != 0


def is_location_on_edge(point: dict, polygon: list[tuple(float, float)], geodesic: bool, tolerance: int) -> bool:
    """
      Computes whether the given point lies on or near the edge of a polygon, within a specified tolerance in meters.
      The polygon edge is composed of great circle segments if geodesic is true, and of Rhumb segments otherwise.
      The polygon edge is implicitly closed -- the closing segment between the first point and the last point is included.

      Ported from Google's android-map-utils PolyUtil class:
      https://github.com/googlemaps/android-maps-utils/blob/master/library/src/main/java/com/google/maps/android/PolyUtil.java
  """
    return __is_location_on_edge_or_path(point, polygon, True, geodesic, tolerance)


def __is_location_on_edge_or_path(point: dict, polygon: list[tuple(float, float)], closed: bool, geodesic: bool, tolerance_earth: int) -> bool:
    idx = __location_index_on_edge_or_path(point, polygon, closed, geodesic, tolerance_earth)
    return idx >= 0


def __location_index_on_edge_or_path(point: dict, poly: list[tuple(float, float)], closed: bool, geodesic: bool, tolerance_earth: int) -> int:
    size = len(poly)
    if size == 0:
        return -1
    tolerance = tolerance_earth / EARTH_RADIUS
    hav_tolerance = hav(tolerance)
    lat3 = to_radians(point['lat'])
    lng3 = to_radians(point['lng'])
    prev = poly[size - 1 if closed else 0]
    lat1 = to_radians(prev[1])
    lng1 = to_radians(prev[0])
    idx = 0
    if geodesic:
        for point2 in poly:
            lat2 = to_radians(point2[1])
            lng2 = to_radians(point2[0])
            if __is_on_segment(lat1, lng1, lat2, lng2, lat3, lng3, hav_tolerance):
                return max(0, idx - 1)
            lat1 = lat2
            lng1 = lng2
            idx += 1
    else:
        min_acceptable = lat3 - tolerance
        max_acceptable = lat3 + tolerance
        y1 = mercator(lat1)
        y3 = mercator(lat3)
        x_try = [None] * 3
        for point2 in poly:
            lat2 = to_radians(point2[1])
            y2 = mercator(lat2)
            lng2 = to_radians(point2[0])
            if max(lat1, lat2) >= min_acceptable and min(lat1, lat2) <= max_acceptable:
                x2 = wrap(lng2 - lng1, -PI, PI)
                x3_base = wrap(lng3 - lng1, -PI, PI)
                x_try[0] = x3_base
                x_try[1] = x3_base + 2 * PI
                x_try[2] = x3_base - 2 * PI
                for x3 in x_try:
                    dy = y2 - y1
                    len2 = x2 * x2 + dy * dy
                    t = 0 if len2 <= 0 else clamp((x3 * x2 + (y3 - y1) * dy) / len2, 0, 1)
                    x_closest = t * x2
                    y_closest = y1 + t * dy
                    lat_closest = inverse_mercator(y_closest)
                    hav_dist = hav_distance(lat3, lat_closest, x3 - x_closest)
                    if hav_dist < hav_tolerance:
                        return max(0, idx - 1)
                    lat1 = lat2
                    lng1 = lng2
                    y1 = y2
                    idx += 1
    return -1


def __is_on_segment(lat1, lng1, lat2, lng2, lat3, lng3, hav_tolerance):
    hav_dist_13 = hav_distance(lat1, lat3, lng1 - lng3)
    if hav_dist_13 <= hav_tolerance:
        return True

    hav_dist23 = hav_distance(lat2, lat3, lng2 - lng3)
    if hav_dist23 <= hav_tolerance:
        return True

    sin_bearing = sin_delta_bearing(lat1, lng1, lat2, lng2, lat3, lng3)
    sin_dist_13 = sin_from_hav(hav_dist_13)
    hav_cross_track = hav_from_sin(sin_dist_13 * sin_bearing)
    if hav_cross_track > hav_tolerance:
        return False

    hav_dist_12 = hav_distance(lat1, lat2, lng1 - lng2)
    term = hav_dist_12 + hav_cross_track * (1 - 2 * hav_dist_12)
    if hav_dist_13 > term or hav_dist23 > term:
        return False
    if hav_dist_12 < 0.74:
        return True

    cos_cross_track = 1 - 2 * hav_cross_track
    hav_along_track13 = (hav_dist_13 - hav_cross_track) / cos_cross_track
    hav_along_track23 = (hav_dist23 - hav_cross_track) / cos_cross_track
    sin_sum_along_track = sin_sum_from_hav(hav_along_track13, hav_along_track23)
    return sin_sum_along_track > 0
