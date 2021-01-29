from route import *
from flask import Flask, render_template, Response
from flask_restful import Resource, Api, reqparse
from persistant_list import PersistentList


class Safepath(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('origin', required=True)
        parser.add_argument('destination', required=True)
        parser.add_argument('method', required=True)
        parser.add_argument('use_edge', required=False)
        parser.add_argument('tolerance', required=False)
        args = parser.parse_args()

        origin = tuple(map(float, args['origin'].split(',')))
        destination = tuple(map(float, args['destination'].split(',')))
        method = args['method']
        use_edge = True if args['use_edge'] is None else False if args['use_edge'] == '0' else True
        tolerance = int(args['tolerance']) if args['tolerance'] is not None else 0

        if use_edge:
            safest_path_edge = best_path_edge(origin, destination, method, total_accidents.get_list(),
                                              tolerance if 5 <= tolerance <= 150 else 20)
            return safest_path_edge
        else:
            safest_path_contains = best_path_contains(origin, destination, method, total_accidents.get_list())
            return safest_path_contains


class Refresh(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('key', required=True)
        args = parser.parse_args()

        if args['key'] == 'CUSTOM GENERATED KEY HERE':
            total_accidents.update()
            return {'refreshed': True, 'len': total_accidents.size()}
        else:
            return {'refreshed': False, 'error': 'Invalid Key'}


class Home(Resource):
    def get(self):
        return Response(response=render_template('index.html'))


app = Flask(__name__)
api = Api(app)
api.add_resource(Safepath, '/safepath')
api.add_resource(Refresh, '/refresh')
api.add_resource(Home, '/')

total_accidents = PersistentList()
total_accidents.update()

if __name__ == '__main__':
    app.run(debug=True)
