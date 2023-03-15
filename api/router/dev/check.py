from flask import Blueprint, request

from api.service.dev.check import update_kiosk_program_status

from api.util.helper.decorator import token_required, nocache
from api.util.reponse_message import response_message_handler

import logging

logger = logging.getLogger(__name__)

check_api = Blueprint('dev_check', __name__)


@check_api.route("/status", methods=["POST"])
@nocache
@token_required
def status():
    """
        1 linear about the route
        A more detaild description of the endpoint
        :return: WelcomeSchema().dump(result), 200
        """
    try:
        return update_kiosk_program_status(data=request.form.to_dict(), header=request.headers)
    except Exception as error:
        logger.critical(error, exc_info=True)
        return response_message_handler(400)

