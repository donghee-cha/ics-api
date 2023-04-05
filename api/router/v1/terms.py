from flask import Blueprint, request

from api.service.v1.terms import get_terms

from api.util.helper.decorator import token_required, nocache
from api.util.reponse_message import response_message_handler

import logging

logger = logging.getLogger(__name__)

terms_api = Blueprint('terms', __name__)


@terms_api.route("/list", methods=["GET", "POST"])
@nocache
@token_required
def list():

    """
        1 linear about the route
        A more detaild description of the endpoint
        :return: WelcomeSchema().dump(result), 200
        """
    try:
        return get_terms(data=request.json, header=request.headers)
    except Exception as error:
        logger.critical(error, exc_info=True)
        return response_message_handler(500)
