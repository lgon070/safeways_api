from csv import *
from route import *

accidents = []


def read_csv():
    with open("la_collisions_2019.csv") as csv_file:
        csv_reader = reader(csv_file)
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
            else:
                accident = {
                    'lat': float(row[1]),
                    'lng': float(row[0]),
                    'severity': int(row[39])
                }
                accidents.append(accident)
                line_count += 1


def search(origin, destination, method, accidents):
    waypoints = best_path_edge(origin, destination, method, accidents)
    # waypoints = best_path_contains(origin, destination, method, accidents)
    if len(waypoints) == 0:
        print(f'No Suitable Path Found')
    else:
        print(f'--------------------------')
        print(f'Returned Points: {waypoints["points"]}')
        print(f'Returned Weight: {waypoints["weight"]}')
        print(f'Returned Route: {waypoints["route"]}')


read_csv()
# to change route and method just update the tuples and string below. First tuple is start location and second is destination
# Los Angeles City Hall to MacArthur Park
search((34.053989, -118.243217), (34.059521, -118.274872), 'bicycling', accidents)
