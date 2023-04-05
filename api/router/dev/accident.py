from flask import Blueprint, request

from api.service.dev.accident import (save_accident_info, get_accident_list)
from api.util.helper.decorator import token_required, nocache
from api.util.reponse_message import response_message_handler

import logging

logger = logging.getLogger(__name__)

accident_api = Blueprint('dev_accident', __name__)


@accident_api.route("/info", methods=["GET", "POST"])
@nocache
@token_required
def info():

    try:
        if request.method == 'GET':
            return get_accident_list(data=request.args.to_dict(), header=request.headers)
        elif request.method == 'POST':
            return save_accident_info(data=request.form.to_dict(), header=request.headers)

    except Exception as error:
        logger.critical(error, exc_info=True)
        return response_message_handler(500)