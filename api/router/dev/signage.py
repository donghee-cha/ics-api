from flask import Blueprint, request

from api.service.dev.signage import get_signage_info

from api.util.helper.decorator import token_required, nocache
from api.util.reponse_message import response_message_handler

import logging

logger = logging.getLogger(__name__)

signage_api = Blueprint('dev_signage', __name__)


@signage_api.route("/info", methods=["GET"])
@nocache
@token_required
def info():

    """
        1 linear about the route
        A more detaild description of the endpoint
        :return: WelcomeSchema().dump(result), 200
        """
    try:
        return get_signage_info(data=request.args.to_dict(), header=request.headers)
    except Exception as error:
        logger.critical(error, exc_info=True)
        return response_message_handler(400)
