from flask import request, render_template, Flask, Response
from persistant_buckets import PersistentBuckets
from route import best_path_contains, best_path_edge

app = Flask(__name__)

persistent_buckets = PersistentBuckets()
persistent_buckets.refresh_all()

print(f'Accidents in Dataset: {persistent_buckets.size_list()}')


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
            return best_path_edge(origin, destination, method, persistent_buckets.get_buckets(),
                                  tolerance if 5 <= tolerance <= 150 else 20)
        else:
            if method is None or not (method == 'walking' or method == 'bicycling' or method == 'driving'):
                method = 'walking'
            return best_path_contains(origin, destination, method, persistent_buckets.get_buckets())
    except Exception as e:
        print(e)
        return {'error_message': 'invalid parameters',
                'parameters': {'origin': origin_param, 'destination': destination_param, 'method': method,
                               'use_edge': use_edge_param, 'tolerance': tolerance_param}}


@app.route('/refresh', methods=['GET'])
def get():
    refresh_type_param = request.args.get('type')
    key = request.args.get('key')
    try:
        refresh_type = 0

        if refresh_type_param is not None:
            refresh_type = int(refresh_type_param)
            if not 0 <= refresh_type <= 2:
                refresh_type = 0

        if key == 'CUSTOM API KEY':
            if refresh_type == 0:
                persistent_buckets.refresh_all()
                return {'refreshed': True, 'buckets_len': persistent_buckets.size_buckets(),
                        'list_len': persistent_buckets.size_list(), 'refresh_type': 'Full Server Refresh'}
            elif refresh_type == 1:
                persistent_buckets.refresh_accidents()
                persistent_buckets.refresh_bucket_accidents()
                return {'refreshed': True,
                        'list_len': persistent_buckets.size_list(), 'refresh_type': 'Accident List Refresh'}
            elif refresh_type == 2:
                persistent_buckets.refresh_buckets()
                persistent_buckets.refresh_bucket_accidents()
                return {'refreshed': True,
                        'buckets_len': persistent_buckets.size_buckets(), 'refresh_type': 'Buckets Dictionary Refresh'}
        else:
            return {'refreshed': False, 'error': 'Invalid Key'}
    except Exception as e:
        print(e)
        return {'error_message': 'invalid/incorrect parameters', 'parameters': {'type': refresh_type_param}}


@app.route('/', methods=['GET'])
def home():
    return Response(response=render_template('index.html'))


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=False)
