from flask import Blueprint, request

from api.service.dev.token import get_auth_token_info
from api.util.helper.decorator import token_required, nocache
from api.util.reponse_message import response_message_handler

import logging

logger = logging.getLogger(__name__)

token_api = Blueprint('dev_token', __name__)


@token_api.route("/info", methods=["GET"])
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
            return get_auth_token_info(data=request.args.to_dict(), header=request.headers)

    except Exception as error:
        logger.critical(error, exc_info=True)
        return response_message_handler(500)
