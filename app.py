from flask import request, render_template, Flask, Response
from persistant_list import PersistentList
from route import best_path_contains, best_path_edge

app = Flask(__name__)

total_accidents = PersistentList()
total_accidents.update()
# total_accidents.test_update()


@app.route('/safepath', methods=['GET'])
def safepath():
    origin_param = request.args.get('origin')
    destination_param = request.args.get('destination')
    method = request.args.get('method')
    use_edge_param = request.args.get('use_edge')
    tolerance_param = request.args.get('tolerance')

    print(f'{origin_param}, {destination_param}, {method}, {use_edge_param}, {tolerance_param}')

    origin = tuple(map(float, origin_param.split(',')))
    destination = tuple(map(float, destination_param.split(',')))
    use_edge = True if use_edge_param is None else False if use_edge_param == '0' else True
    tolerance = int(tolerance_param) if tolerance_param is not None else 0

    # https://polar-hollows-98491.herokuapp.com/safepath?origin=34.053715,-118.242653&destination=34.059238,-118.279068&method=walking
    if use_edge:
        safest_path_edge = best_path_edge(origin, destination, method, total_accidents.get_list(), tolerance if 5 <= tolerance <= 150 else 20)
        return safest_path_edge
    else:
        safest_path_contains = best_path_contains(origin, destination, method, total_accidents.get_list())
        return safest_path_contains


@app.route('/refresh', methods=['GET'])
def get():
    key = request.args.get('key')
    if key == '1234':
        total_accidents.update()
        # total_accidents.test_update()
        return {'refreshed': True, 'len': total_accidents.size()}
    else:
        return {'refreshed': False, 'error': 'Invalid Key'}


@app.route('/', methods=['GET'])
def home():
    return Response(response=render_template('index.html'))


if __name__ == '__main__':
    app.run()
