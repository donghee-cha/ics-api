from flask import Blueprint, request

from api.service.v1.counting import set_counting_print_count

from api.util.helper.decorator import token_required, nocache
from api.util.reponse_message import response_message_handler

import logging

logger = logging.getLogger(__name__)

counting_api = Blueprint('counting', __name__)


@counting_api.route("/print", methods=["POST"])
@nocache
@token_required
def print():
    """
        1 linear about the route
        A more detaild description of the endpoint
        :return: WelcomeSchema().dump(result), 200
        """
    try:
        return set_counting_print_count(data=request.form.to_dict(), header=request.headers)
    except Exception as error:
        logger.critical(error, exc_info=True)
        return response_message_handler(500)

