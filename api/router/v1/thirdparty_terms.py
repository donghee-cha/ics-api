from flask import Blueprint, request

from api.service.v1.thirdparty_terms import get_thirdparty_terms

from api.util.helper.decorator import token_required, nocache
from api.util.reponse_message import response_message_handler

import logging

logger = logging.getLogger(__name__)

thirdparty_terms_api = Blueprint('thirdparty_terms', __name__)


@thirdparty_terms_api.route("/list", methods=["GET"])
@nocache
@token_required
def list():

    """
        1 linear about the route
        A more detaild description of the endpoint
        :return: WelcomeSchema().dump(result), 200
        """
    try:
        return get_thirdparty_terms(data=request.args.to_dict(), header=request.headers)
    except Exception as error:
        logger.critical(error, exc_info=True)
        return response_message_handler(500)
