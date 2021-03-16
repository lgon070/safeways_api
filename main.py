from flask import request, render_template, Flask, Response
from persistant_list import PersistentList
from route import best_path_contains, best_path_edge

app = Flask(__name__)

total_accidents = PersistentList()
total_accidents.update()
print(f'Accidents in Dataset: {total_accidents.size()}')


# total_accidents.test_update()


@app.route('/safepath', methods=['GET'])
def safepath():
    origin_param = request.args.get('origin')
    destination_param = request.args.get('destination')
    method = request.args.get('method')
    use_edge_param = request.args.get('use_edge')
    tolerance_param = request.args.get('tolerance')

    try:
        origin = tuple(map(float, origin_param.split(',')))
        destination = tuple(map(float, destination_param.split(',')))
        use_edge = True if use_edge_param is None else False if use_edge_param == '0' else True
        tolerance = int(tolerance_param) if tolerance_param is not None else 0

        if use_edge:
            if method is None or not (method == 'walking' or method == 'bicycling' or method == 'driving'):
                method = 'walking'
            return best_path_edge(origin, destination, method, total_accidents.get_list(),
                                  tolerance if 5 <= tolerance <= 150 else 20)
        else:
            if method is None or not (method == 'walking' or method == 'bicycling' or method == 'driving'):
                method = 'walking'
            return best_path_contains(origin, destination, method, total_accidents.get_list())
    except Exception as e:
        print(e)
        return {'error_message': 'invalid parameters',
                'parameters': {'origin': origin_param, 'destination': destination_param, 'method': method,
                               'use_edge': use_edge_param, 'tolerance': tolerance_param}}


@app.route('/refresh', methods=['GET'])
def get():
    key = request.args.get('key')
    if key == 'CUSTOM API KEY':
        total_accidents.update()
        return {'refreshed': True, 'len': total_accidents.size()}
    else:
        return {'refreshed': False, 'error': 'Invalid Key'}


@app.route('/', methods=['GET'])
def home():
    return Response(response=render_template('index.html'))


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=False)
