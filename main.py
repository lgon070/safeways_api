from csv import *
from route import *


def read_csv() -> List[dict]:
    total_accidents = []
    with open("la_collisions_2019.csv") as csv_file:
        csv_reader = reader(csv_file)
        readable_values = False
        for row in csv_reader:
            if readable_values:
                total_weight = 0.0
                latitude = 0.0
                longitude = 0.0

                # Save latitude and longitude to its respective variables
                # Lat and Lng set to 0.0 in case we encounter an issue reading lat and lng from CSV, we simply do not add  this accident to list
                try:
                    latitude = float(row[1])
                    longitude = float(row[0])
                except Exception as e:
                    print(e)

                if latitude != 0.0 and longitude != 0.0:
                    # Collision Severity - overall severity of the accident
                    # Weight: Given by row data
                    # Notes: Scale of 0-4
                    # print(f'Collision severity: {row[39]}')
                    try:
                        collision_severity = 0.0 if row[39] == '0' or row[39] == '' else float(row[39])
                        total_weight += collision_severity
                    except Exception as e:
                        print(e)

                    # Number Killed - number of vehicle occupants killed in accident
                    # Weight - 10 per death
                    # Notes:
                    # print(f'Number Killed: {row[40]}')
                    try:
                        number_killed = 0.0 if row[40] == '0' or row[40] == '' else float(row[40]) * 10
                        total_weight += number_killed
                    except Exception as e:
                        print(e)

                    # Number Injured - number of vehicle occupants injured in accident
                    # Weight: 5 per injury
                    # Notes:
                    # print(f'Number Injured: {row[41]}')
                    try:
                        number_injured = 0.0 if row[41] == '0' or row[41] == '' else float(row[41]) * 5
                        total_weight += number_injured
                    except Exception as e:
                        print(e)

                    # Hit and Run - if the accident involved a hit and run: Weight
                    # Weight: 3 for hit and run, 0 for no hit and run
                    # Notes: F denotes Female, M denotes Male, N denotes None
                    # print(f'Hit and Run: {row[48]}')
                    try:
                        hit_and_run = 3 if row[48].upper() == 'M' or row[48].upper() == 'F' else 0
                        total_weight += hit_and_run
                    except Exception as e:
                        print(e)

                    # Pedestrian Accident - whether or not pedestrians where involved in accident
                    # Weight: 3 for yes, 0 for no
                    # Notes: Y denotes yes, empty denotes no
                    # print(f'Pedestrian Accident: {row[58]}')
                    try:
                        pedestrian_accident = 3 if row[58].upper() == 'Y' or row[58].upper() == 'YES' else 0
                        total_weight += pedestrian_accident
                    except Exception as e:
                        print(e)

                    # Bicycle Accident - whether or not bicyclists where involved in accident
                    # Weight: 3 for yes, 0 for no
                    # Notes: Y denotes yes, empty denotes no
                    # print(f'Bicycle Accident: {row[59]}')
                    try:
                        bicycle_accident = 3 if row[59].upper() == 'Y' or row[58].upper() == 'YES' else 0
                        total_weight += bicycle_accident
                    except Exception as e:
                        print(e)

                    # Motorcycle Accident - whether or not motorcycles where involved in accident
                    # Weight: 2 for yes, 0 for no
                    # Notes: Y denotes yes, empty denotes no
                    # print(f'Motorcycle Accident: {row[60]}')
                    try:
                        motorcycle_accident = 2 if row[60].upper() == 'Y' or row[60].upper() == 'YES' else 0
                        total_weight += motorcycle_accident
                    except Exception as e:
                        print(e)

                    # Truck Accident - whether or not trucks where involved in accident
                    # Weight: 4 for yes, 0 for no
                    # Notes: Y denotes yes, empty denotes no
                    # print(f'Truck Accident: {row[61]}')
                    try:
                        truck_accident = 4 if row[61].upper() == 'Y' or row[61].upper() == 'YES' else 0
                        total_weight += truck_accident
                    except Exception as e:
                        print(e)

                    # Alcohol Involved - whether or not alcohol was involved in accident
                    # Weight: 5 for yes, 0 for no
                    # Notes: Y denotes yes, empty denotes no
                    # print(f'Alcohol Involved: {row[63]}')
                    try:
                        alcohol_involved = 4 if row[63].upper() == 'Y' or row[63].upper() == 'YES' else 0
                        total_weight += alcohol_involved
                    except Exception as e:
                        print(e)

                    # Count Severe Inj - number of severe injuries from accident
                    # Weight: 5 per injury
                    # Notes:
                    # print(f'Count Severe Inj: {row[66]}')
                    try:
                        count_severe_inj = 0.0 if row[66] == '0' or row[66] == '' else float(row[39]) * 5
                        total_weight += count_severe_inj
                    except Exception as e:
                        print(e)

                    # Count Visible Inj - number of visible injuries from accident
                    # Weight: 3 per injury
                    # Notes:
                    # print(f'Count Visible Inj: {row[67]}')
                    try:
                        count_visible_inj = 0.0 if row[67] == '0' or row[67] == '' else float(row[67]) * 3
                        total_weight += count_visible_inj
                    except Exception as e:
                        print(e)

                    # Count Complaint Pain - number of pain complaints from accident
                    # Weight: 1 per complaint
                    # Notes:
                    # print(f'Count Complaint Pain: {row[68]}')
                    try:
                        count_complaint_pain = 0.0 if row[68] == '0' or row[68] == '' else float(row[68])
                        total_weight += count_complaint_pain
                    except Exception as e:
                        print(e)

                    # Count Ped Killed - number of pedestrians who were killed in accident
                    # Weight: 10 per death
                    # Notes:
                    # print(f'Count Ped Killed: {row[69]}')
                    try:
                        count_ped_killed = 0.0 if row[69] == '0' or row[69] == '' else float(row[69]) * 10
                        total_weight += count_ped_killed
                    except Exception as e:
                        print(e)

                    # Count Ped Injured - number of pedestrians injured in accident
                    # Weight: 5 per injury
                    # Notes:
                    # print(f'Count Ped Injured: {row[70]}')
                    try:
                        count_ped_injured = 0.0 if row[70] == '0' or row[70] == '' else float(row[70]) * 5
                        total_weight += count_ped_injured
                    except Exception as e:
                        print(e)

                    # Count Bicyclist Killed - number of bicyclists killed in accident
                    # Weight: 10 per death
                    # Notes:
                    # print(f'Count Bicyclist Killed: {row[71]}')
                    try:
                        count_bicyclist_killed = 0.0 if row[71] == '0' or row[71] == '' else float(row[71]) * 10
                        total_weight += count_bicyclist_killed
                    except Exception as e:
                        print(e)

                    # Count Bicyclist Injured - number of bicyclists injured in accident
                    # Weight: 5 per injury
                    # Notes:
                    # print(f'Count Bicyclist Injured: {row[72]}')
                    try:
                        count_bicyclist_injured = 0.0 if row[72] == '0' or row[72] == '' else float(row[72]) * 5
                        total_weight += count_bicyclist_injured
                    except Exception as e:
                        print(e)

                    # Count MC Killed - number of motorcyclists killed in accident
                    # Weight: 10 per death
                    # Notes:
                    # print(f'Count MC Killed: {row[73]}')
                    try:
                        count_mc_killed = 0.0 if row[73] == '0' or row[73] == '' else float(row[73]) * 10
                        total_weight += count_mc_killed
                    except Exception as e:
                        print(e)

                    # Count MC Injured - number of motorcyclists injured in accident
                    # Weight: 5 per injury
                    # Notes:
                    # print(f'Count MC Injured: {row[74]}')
                    try:
                        count_mc_injured = 0.0 if row[74] == '0' or row[74] == '' else float(row[74]) * 5
                        total_weight += count_mc_injured
                    except Exception as e:
                        print(e)
                    total_accidents.append({
                        'lat': latitude,
                        'lng': longitude,
                        'total_weight': total_weight
                    })
            else:
                readable_values = True
    return total_accidents


def search(origin, destination, method, accidents):
    # waypoints = best_path_edge(origin, destination, method, accidents)
    waypoints = best_path_contains(origin, destination, method, accidents)
    if len(waypoints) == 0:
        print(f'No Suitable Path Found')
    else:
        print(f'--------------------------')
        print(f'Returned Points: {waypoints["points"]}')
        print(f'Returned Weight: {waypoints["weight"]}')
        print(f'Returned Route: {waypoints["route"]}')


accidents = read_csv()
# to change route and method just update the tuples and string below. First tuple is start location and second is destination
# Los Angeles City Hall to MacArthur Park
search((34.053989, -118.243217), (34.059521, -118.274872), 'bicycling', accidents)
