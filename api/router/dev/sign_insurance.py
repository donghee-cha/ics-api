from flask import Blueprint, request

from api.service.dev.sign_insurance import save_sign_insurance_find, save_sign_insurance_info, update_sign_insurance_result

from api.util.helper.decorator import token_required, nocache
from api.util.reponse_message import response_message_handler

import logging

logger = logging.getLogger(__name__)

sign_insurance_api = Blueprint('dev_sign_insurance', __name__)


@sign_insurance_api.route("/find", methods=["POST"])
@nocache
@token_required
def find():
    """
        1 linear about the route
        A more detaild description of the endpoint
        :return: WelcomeSchema().dump(result), 200
        """
    try:
        return save_sign_insurance_find(data=request.form.to_dict(), header=request.headers)
    except Exception as error:
        logger.critical(error, exc_info=True)
        return response_message_handler(500)


@sign_insurance_api.route("/info", methods=["POST"])
@nocache
@token_required
def info():
    """
        1 linear about the route
        A more detaild description of the endpoint
        :return: WelcomeSchema().dump(result), 200
        """
    try:
        return save_sign_insurance_info(data=request.form.to_dict(), header=request.headers)
    except Exception as error:
        logger.critical(error, exc_info=True)
        return response_message_handler(500)


@sign_insurance_api.route("/result", methods=["POST"])
@nocache
@token_required
def result():

    try:
        return update_sign_insurance_result(data=request.form.to_dict(), header=request.headers)
    except Exception as error:
        logger.critical(error, exc_info=True)
        return response_message_handler(500)
