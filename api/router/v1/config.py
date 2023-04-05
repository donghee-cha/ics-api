from flask import Blueprint, request

from api.service.v1.config import get_config_info, set_config_info

from api.util.helper.decorator import token_required, nocache
from api.util.reponse_message import response_message_handler

import logging

logger = logging.getLogger(__name__)

config_api = Blueprint('config', __name__)


@config_api.route("/info", methods=["GET", "POST"])
@nocache
@token_required
def info():

    try:
        if request.method == 'GET':
            return get_config_info(data=request.args.to_dict(), header=request.headers)
        elif request.method == 'POST':
            return set_config_info(data=request.form.to_dict(), header=request.headers)

    except Exception as error:
        logger.critical(error, exc_info=True)
        return response_message_handler(500)

