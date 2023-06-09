from flask import Blueprint, request

from api.service.v1.send import save_send_notification

from api.util.helper.decorator import token_required, nocache
from api.util.reponse_message import response_message_handler

import logging

logger = logging.getLogger(__name__)

send_api = Blueprint('send', __name__)


@send_api.route("/notification", methods=["POST"])
@nocache
@token_required
def notification():
    """
        1 linear about the route
        A more detaild description of the endpoint
        :return: WelcomeSchema().dump(result), 200
        """
    try:
        return save_send_notification(data=request.form.to_dict(), header=request.headers)
    except Exception as error:
        logger.critical(error, exc_info=True)
        return response_message_handler(500)
