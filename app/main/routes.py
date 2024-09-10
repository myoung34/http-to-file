""" all routes will end up here or loaded here for flask """
# pylint:disable=cyclic-import
import base64
import os
from uuid import uuid4

from flask import jsonify, request

from app.main import BP as blueprint


@blueprint.route('/', methods=['POST'])
def main_route():
    """ Main route """
    if request.headers.get('Authorization') == f'Bearer {os.environ.get("API_KEY")}':
        file_dir = os.environ.get('FILE_DIR', '/tmp')
        file_uuid = str(uuid4())
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)
        with open(f'{file_dir}/{file_uuid}.log', 'w') as file: # pylint:disable=unspecified-encoding
            # if request.json['base64'] is '[tT]rue' write the decoded base64 to the file only
            if request.json.get('base64', 'false').lower() == 'true':
                message = base64.b64decode(request.json['data']).decode('utf-8')
                file.write(message)
            else:
                file.write(str(request.json))
        return jsonify({'status': 'ok', 'id': file_uuid}), 200
    return jsonify({'status': 'unauthorized'}), 401

@blueprint.route('/expel', methods=['POST'])
def expel_route():
    """ Main route """
    passthrough_header = os.environ.get('PASSTHROUGH_HEADER', uuid4())
    passthrough_delimiter = os.environ.get('PASSTHROUGH_DELIMITER', '=')

    if request.headers.get(passthrough_header) and request.headers.get('passthrough_header') != '': # pylint:disable=line-too-long
        file_dir = os.environ.get('FILE_DIR', '/tmp')
        file_name = request.headers.get(passthrough_header).split(passthrough_delimiter)[1]

        if not os.path.exists(file_dir):
            os.makedirs(file_dir)

        with open(f'{file_dir}/{file_name}.log', 'w') as file:  # pylint:disable=unspecified-encoding
            # write the raw POST data to a file
            file.write(request.data)
        return jsonify({'status': 'ok', 'id': file_name}), 200
    return jsonify({'status': 'not found'}), 404
