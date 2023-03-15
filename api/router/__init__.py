import gc
import json
import logging

from flask import Blueprint, send_file, request

from api.config import contents_path
from api.service import save_file
from api.util.helper.decorator import nocache, token_required
from api.util.reponse_message import response_message_handler

import yaml, os

common_api = Blueprint('/', __name__)

logger = logging.getLogger(__name__)


@common_api.route('/')
@common_api.route('/<path:path>', methods=["GET", "POST"])
@nocache
def index(path=None):
    """
    1 linear about the route
    A more detaild description of the endpoint
    :return: WelcomeSchema().dump(result), 200
    """
    if path == 'swagger.json':
        with open(f'{os.getcwd()}\\api\\templates\\swagger.json', 'r') as file:
            data = file.read()
        return json.loads(data)
    else:
        return response_message_handler(404)


@common_api.route('/contents-upload/<path:path>', methods=["POST"])
@nocache
@token_required
def contents_upload(path=None):

    try:
        return save_file(request, path)
    except Exception as error:
        logger.critical(error, exc_info=True)
        return response_message_handler(400)


@common_api.route('/contents/<path:path>', methods=["GET", "POST"])
@nocache
def contents(path=None):
    """
    1 linear about the route
    A more detaild description of the endpoint
    :return: WelcomeSchema().dump(result), 200
    """
    # print(category)
    logger.info(f'{contents_path}/{path}')

    return send_file(f'{contents_path}/{path}', as_attachment=True)


@common_api.errorhandler(404)
def page_not_found():
    return response_message_handler(404)


@common_api.errorhandler(400)
def page_not_found():
    return response_message_handler(400)


@common_api.errorhandler(405)
def page_not_found():
    return response_message_handler(405)


@common_api.errorhandler(500)
def page_not_found():
    return response_message_handler(500)
