from flask import Blueprint, request

from api.service.v1.claim import get_insurance_claim_info, save_documentary

from api.util.helper.decorator import token_required, nocache
from api.util.reponse_message import response_message_handler

import logging

logger = logging.getLogger(__name__)

claim_api = Blueprint('claim', __name__)


@claim_api.route("/info", methods=["GET"])
@nocache
@token_required
def info():

    try:
        if request.method == 'GET':
            return get_insurance_claim_info(data=request.args.to_dict(), header=request.headers)

    except Exception as error:
        logger.critical(error, exc_info=True)
        return response_message_handler(500)


@claim_api.route("/documentary", methods=["POST"])
@nocache
@token_required
def documentary():
    """
        1 linear about the route
        A more detaild description of the endpoint
        :return: WelcomeSchema().dump(result), 200
        """

    try:
        if request.method == 'POST':
            return save_documentary(data=request.form.to_dict(), header=request.headers)

    except Exception as error:
        logger.critical(error, exc_info=True)
        return response_message_handler(500)
