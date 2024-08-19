""" all routes will end up here or loaded here for flask """
# pylint:disable=cyclic-import
import os
from uuid import uuid4

from flask import jsonify, request

from app.main import BP as blueprint


@blueprint.route('/', methods=['POST'])
def main_route():
    """ Main route """
    if request.headers.get('Authorization') == f'Bearer {os.environ.get("API_KEY")}':
        file_dir = os.environ.get('FILE_DIR', '/tmp')
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)
        with open(f'{file_dir}/{str(uuid4())}.log', 'w') as file: # pylint:disable=unspecified-encoding
            file.write(str(request.json))
        return jsonify({'status': 'ok'}), 200
    return jsonify({'status': 'unauthorized'}), 401
