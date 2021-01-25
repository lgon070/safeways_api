import route
from flask import Flask
from flask_restful import Resource, Api, reqparse
from persistant_list import PersistentList
from global_data import GlobalData


class Safepath(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('origin', required=True)
        parser.add_argument('destination', required=True)
        parser.add_argument('method', required=True)
        parser.add_argument('use_edge', required=False)
        parser.add_argument('tolerance', required=False)
        args = parser.parse_args()

        # to change route and method just update the tuples and string below. First tuple is start location and second is destination
        # Los Angeles City Hall to MacArthur Park
        # http://127.0.0.1:5000/safepath?origin=34.053989,-118.243217&destination=34.059521,-118.274872&method=bicycling
        # http://127.0.0.1:5000/safepath?origin=34.053989,-118.243217&destination=34.059521,-118.274872&method=bicycling&use_edge=0&tolerance=25
        # http://127.0.0.1:5000/safepath?origin=34.053989,-118.243217&destination=34.059521,-118.274872&method=bicycling&use_edge=1&tolerance=25000

        origin = tuple(map(float, args['origin'].split(',')))
        destination = tuple(map(float, args['destination'].split(',')))
        method = args['method']
        use_edge = True if args['use_edge'] is None else False if args['use_edge'] == '0' else True
        tolerance = int(args['tolerance']) if args['tolerance'] is not None else 0

        if use_edge:
            safest_path_edge = route.best_path_edge(origin, destination, method, total_accidents.get_list(),
                                                    tolerance if 5 <= tolerance <= 150 else 15)
            return safest_path_edge
        else:
            safest_path_contains = route.best_path_contains(origin, destination, method, total_accidents.get_list())
            return safest_path_contains


class Refresh(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('key', required=True)
        args = parser.parse_args()

        # http://127.0.0.1:5000/refresh?key=jJKq7vwFcX8CeCL
        gd = GlobalData()
        if gd.refresh_key() == args['key']:
            total_accidents.update()
            return {'refreshed': True, 'len': total_accidents.size()}
        else:
            return {'refreshed': False, 'error': 'Invalid Key'}


app = Flask(__name__)
api = Api(app)
api.add_resource(Safepath, '/safepath')
api.add_resource(Refresh, '/refresh')

total_accidents = PersistentList()
total_accidents.update()

if __name__ == '__main__':
    app.run(debug=True)
