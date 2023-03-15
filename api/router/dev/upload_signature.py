from flask import Blueprint, request

from api.service.dev.upload_signature import upload_signature_insurant, upload_signature_beneficiary

from api.util.helper.decorator import token_required, nocache
from api.util.reponse_message import response_message_handler

import logging

logger = logging.getLogger(__name__)

upload_signature_api = Blueprint('dev_upload-signature', __name__)


@upload_signature_api.route("/insurant", methods=["POST"])
@nocache
@token_required
def insurant():
    """
        1 linear about the route
        A more detaild description of the endpoint
        :return: WelcomeSchema().dump(result), 200
        """
    try:
        return upload_signature_insurant(data=request.form.to_dict(), header=request.headers)
    except Exception as error:
        logger.critical(error, exc_info=True)
        return response_message_handler(400)


@upload_signature_api.route("/beneficiary", methods=["POST"])
@nocache
@token_required
def beneficiary():
    """
        1 linear about the route
        A more detaild description of the endpoint
        :return: WelcomeSchema().dump(result), 200
        """
    try:
        return upload_signature_beneficiary(data=request.form.to_dict(), header=request.headers)
    except Exception as error:
        logger.critical(error, exc_info=True)
        return response_message_handler(400)
