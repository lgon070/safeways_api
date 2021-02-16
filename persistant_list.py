import requests
from requests.exceptions import HTTPError


class PersistentList:
    def __init__(self):
        self.list = []
        self.features = []

    def update(self):
        try:
            response = requests.get('https://services1.arcgis.com/tp9wqSVX1AitKgjd/arcgis/rest/services/rsg20132018_gdb/FeatureServer/0/query?where=1%3D1&outFields=int_id,collision_severity,number_killed,hit_and_run,pedestrian_accident,motorcycle_accident,truck_accident,alcohol_involved,count_severe_inj,count_visible_inj,count_complaint_pain,count_ped_killed,count_ped_injured,count_bicyclist_killed,count_bicyclist_injured,count_mc_killed,latitude,longitude,point_x,point_y,count_mc_injured,bicycle_accident,number_injured&returnGeometry=false&outSR=4326&f=json')
            # response = requests.get('https://opendata.arcgis.com/datasets/66d96f15d4e14e039caa6134e6eab8e5_0.geojson')
            response.raise_for_status()
            json_data = response.json()
            dataset = json_data['features']
            for data in dataset:
                accident = data['attributes']
                # accident = data['properties']
                accident_weight = 0
                latitude = 0
                longitude = 0
                int_id = accident['int_id']

                try:
                    latitude = float(accident['point_y'])
                    longitude = float(accident['point_x'])
                except Exception as e:
                    print(f'Could not read lat and lng of accident. Skipped accident')
                    print(e)

                if latitude != 0 and longitude != 0:
                    # Collision Severity - overall severity of the accident
                    # Weight: Given by row data
                    # Notes: Scale of 0-4
                    # print(f'Collision severity: {accident['collision_severity'}')
                    try:
                        collision_severity_val = accident['collision_severity']
                        collision_severity = 0 if collision_severity_val == '0' or collision_severity_val == '' or collision_severity_val is None else collision_severity_val
                        accident_weight += collision_severity
                    except Exception as e:
                        print(e)

                    # Number Killed - number of vehicle occupants killed in accident
                    # Weight - 10 per death
                    # Notes:
                    # print(f'Number Killed: {number_killed_val}')
                    try:
                        number_killed_val = accident['number_killed']
                        number_killed = 0 if number_killed_val == '0' or number_killed_val == '' or number_killed_val is None else number_killed_val * 10
                        accident_weight += number_killed
                    except Exception as e:
                        print(e)

                    # Number Injured - number of vehicle occupants injured in accident
                    # Weight: 5 per injury
                    # Notes:
                    # print(f'Number Injured: {number_injured_val}')
                    try:
                        number_injured_val = accident['number_injured']
                        number_injured = 0 if number_injured_val == '0' or number_injured_val == '' or number_injured_val is None else number_injured_val * 5
                        accident_weight += number_injured
                    except Exception as e:
                        print(e)

                    # Hit and Run - if the accident involved a hit and run: Weight
                    # Weight: 3 for hit and run, 0 for no hit and run
                    # Notes: F denotes Female, M denotes Male, N denotes No One
                    # print(f'Hit and Run: {row[48]}')
                    try:
                        hit_and_run_val = accident['hit_and_run']
                        hit_and_run = 0 if hit_and_run_val == 'N' else 3
                        accident_weight += hit_and_run
                    except Exception as e:
                        print(e)

                    # Pedestrian Accident - whether or not pedestrians where involved in accident
                    # Weight: 3 for yes, 0 for no
                    # Notes: Y denotes yes, empty denotes no
                    # print(f'Pedestrian Accident: {row[58]}')
                    try:
                        pedestrian_accident_val = accident['pedestrian_accident']
                        pedestrian_accident = 0 if pedestrian_accident_val == 'N' else 3
                        accident_weight += pedestrian_accident
                    except Exception as e:
                        print(e)

                    # Bicycle Accident - whether or not bicyclists where involved in accident
                    # Weight: 3 for yes, 0 for no
                    # Notes: Y denotes yes, empty denotes no
                    # print(f'Bicycle Accident: {row[59]}')
                    try:
                        bicycle_accident_val = accident['bicycle_accident']
                        bicycle_accident = 0 if bicycle_accident_val == 'N' else 3
                        accident_weight += bicycle_accident
                    except Exception as e:
                        print(e)

                    # Motorcycle Accident - whether or not motorcycles where involved in accident
                    # Weight: 2 for yes, 0 for no
                    # Notes: Y denotes yes, empty denotes no
                    # print(f'Motorcycle Accident: {row[60]}')
                    try:
                        motorcycle_accident_val = accident['motorcycle_accident']
                        motorcycle_accident = 0 if motorcycle_accident_val == 'N' else 2
                        accident_weight += motorcycle_accident
                    except Exception as e:
                        print(e)

                    # Truck Accident - whether or not trucks where involved in accident
                    # Weight: 4 for yes, 0 for no
                    # Notes: Y denotes yes, empty denotes no
                    # print(f'Truck Accident: {row[61]}')
                    try:
                        truck_accident_val = accident['truck_accident']
                        truck_accident = 0 if truck_accident_val == 'N' else 4
                        accident_weight += truck_accident
                    except Exception as e:
                        print(e)

                    # Alcohol Involved - whether or not alcohol was involved in accident
                    # Weight: 5 for yes, 0 for no
                    # Notes: Y denotes yes, empty denotes no
                    # print(f'Alcohol Involved: {row[63]}')
                    try:
                        alcohol_involved_val = accident['alcohol_involved']
                        alcohol_involved = 0 if alcohol_involved_val == 'N' else 5
                        accident_weight += alcohol_involved
                    except Exception as e:
                        print(e)

                    # Count Severe Inj - number of severe injuries from accident
                    # Weight: 5 per injury
                    # Notes:
                    # print(f'Count Severe Inj: {count_severe_inj_val}')
                    try:
                        count_severe_inj_val = accident['count_severe_inj']
                        count_severe_inj = 0 if count_severe_inj_val == '0' or count_severe_inj_val == '' or count_severe_inj_val is None else count_severe_inj_val * 5
                        accident_weight += count_severe_inj
                    except Exception as e:
                        print(e)

                    # Count Visible Inj - number of visible injuries from accident
                    # Weight: 3 per injury
                    # Notes:
                    # print(f'Count Visible Inj: {count_visible_inj}')
                    try:
                        count_visible_inj_val = accident['count_visible_inj']
                        count_visible_inj = 0 if count_visible_inj_val == '0' or count_visible_inj_val == '' or count_visible_inj_val is None else count_visible_inj_val * 3
                        accident_weight += count_visible_inj
                    except Exception as e:
                        print(e)

                    # Count Complaint Pain - number of pain complaints from accident
                    # Weight: 1 per complaint
                    # Notes:
                    # print(f'Count Complaint Pain: {count_complaint_pain_val}')
                    try:
                        count_complaint_pain_val = accident['count_complaint_pain']
                        count_complaint_pain = 0 if count_complaint_pain_val == '0' or count_complaint_pain_val == '' or count_complaint_pain_val else count_complaint_pain_val
                        accident_weight += count_complaint_pain
                    except Exception as e:
                        print(e)

                    # Count Ped Killed - number of pedestrians who were killed in accident
                    # Weight: 10 per death
                    # Notes:
                    # print(f'Count Ped Killed: {count_ped_killed_val}')
                    try:
                        count_ped_killed_val = accident['count_ped_killed']
                        count_ped_killed = 0 if count_ped_killed_val == '0' or count_ped_killed_val == '' or count_ped_killed_val is None else count_ped_killed_val * 10
                        accident_weight += count_ped_killed
                    except Exception as e:
                        print(e)

                    # Count Ped Injured - number of pedestrians injured in accident
                    # Weight: 5 per injury
                    # Notes:
                    # print(f'Count Ped Injured: {count_ped_injured_val}')
                    try:
                        count_ped_injured_val = accident['count_ped_injured']
                        count_ped_injured = 0 if count_ped_injured_val == '0' or count_ped_injured_val == '' or count_ped_injured_val is None else count_ped_injured_val * 5
                        accident_weight += count_ped_injured
                    except Exception as e:
                        print(e)

                    # Count Bicyclist Killed - number of bicyclists killed in accident
                    # Weight: 10 per death
                    # Notes:
                    # print(f'Count Bicyclist Killed: {count_bicyclist_killed_val}')
                    try:
                        count_bicyclist_killed_val = accident['count_bicyclist_killed']
                        count_bicyclist_killed = 0 if count_bicyclist_killed_val == '0' or count_bicyclist_killed_val == '' or count_bicyclist_killed_val is None else count_bicyclist_killed_val * 10
                        accident_weight += count_bicyclist_killed
                    except Exception as e:
                        print(e)

                    # Count Bicyclist Injured - number of bicyclists injured in accident
                    # Weight: 5 per injury
                    # Notes:
                    # print(f'Count Bicyclist Injured: {count_bicyclist_injured_val}')
                    try:
                        count_bicyclist_injured_val = accident['count_bicyclist_injured']
                        count_bicyclist_injured = 0 if count_bicyclist_injured_val == '0' or count_bicyclist_injured_val == '' or count_bicyclist_injured_val is None else count_bicyclist_injured_val * 5
                        accident_weight += count_bicyclist_injured
                    except Exception as e:
                        print(e)

                    # Count MC Killed - number of motorcyclists killed in accident
                    # Weight: 10 per death
                    # Notes:
                    # print(f'Count MC Killed: {count_mc_killed_val}')
                    try:
                        count_mc_killed_val = accident['count_mc_killed']
                        count_mc_killed = 0 if count_mc_killed_val == '0' or count_mc_killed_val == '' or count_mc_killed_val is None else count_mc_killed_val * 10
                        accident_weight += count_mc_killed
                    except Exception as e:
                        print(e)

                    # Count MC Injured - number of motorcyclists injured in accident
                    # Weight: 5 per injury
                    # Notes:
                    # print(f'Count MC Injured: {count_mc_injured_val}')
                    try:
                        count_mc_injured_val = accident['count_mc_injured']
                        count_mc_injured = 0 if count_mc_injured_val == '0' or count_mc_injured_val == '' or count_mc_injured_val is None else count_mc_injured_val * 5
                        accident_weight += count_mc_injured
                    except Exception as e:
                        print(e)

                    self.append({
                        'accident_id': int_id,
                        'lat': latitude,
                        'lng': longitude,
                        'accident_weight': accident_weight
                    })
            print('Success! List refreshed with new dataset')
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}\nPrevented List refresh')
        except Exception as e:
            print(f'Other error occurred: {e}\nPrevented List refresh')

    def test_update(self):
        return []

    def append(self, to_append):
        self.list.append(to_append)

    def get_list(self):
        return self.list

    def replace(self, new_list):
        self.list = new_list

    def clear(self):
        self.list.clear()

    def size(self):
        return len(self.list)
