from flask import Blueprint, request

from api.service.v1.insurance import save_insurance_list, get_insurance_list

from api.util.helper.decorator import token_required, nocache
from api.util.reponse_message import response_message_handler

import logging

logger = logging.getLogger(__name__)

insurance_api = Blueprint('insurance', __name__)


@insurance_api.route("/info", methods=["GET", "POST"])
@nocache
@token_required
def info():
    """
        1 linear about the route
        A more detaild description of the endpoint
        :return: WelcomeSchema().dump(result), 200
        """

    try:
        if request.method == 'GET':
            return get_insurance_list(data=request.args.to_dict(), header=request.headers)
        elif request.method == 'POST':
            return save_insurance_list(data=request.form.to_dict(), header=request.headers)

    except Exception as error:
        logger.critical(error, exc_info=True)
        return response_message_handler(400)
