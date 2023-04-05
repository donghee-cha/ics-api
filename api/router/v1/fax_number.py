from flask import Blueprint, request

from api.service.v1.fax_number import save_fax_number, get_fax_number

from api.util.helper.decorator import token_required, nocache
from api.util.reponse_message import response_message_handler

import logging

logger = logging.getLogger(__name__)

fax_number_api = Blueprint('fax-number', __name__)


@fax_number_api.route("/info", methods=["POST", "GET"])
@nocache
@token_required
def info():

    try:
        if request.method == 'POST':
            return save_fax_number(data=request.form.to_dict(), header=request.headers)
        elif request.method == 'GET':
            return get_fax_number(data=request.args.to_dict(), header=request.headers)

    except Exception as error:
        logger.critical(error, exc_info=True)
        return response_message_handler(500)
