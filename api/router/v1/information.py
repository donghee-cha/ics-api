from flask import Blueprint, request

from api.service.v1.information import (get_insurance_company_list, get_bank_company_list, get_hospital_info,
                                        get_work_list)
from api.util.helper.decorator import token_required, nocache
from api.util.reponse_message import response_message_handler

import logging

logger = logging.getLogger(__name__)

information_api = Blueprint('information', __name__)


@information_api.route("/insurance", methods=["GET"])
@nocache
@token_required
def insurance_info():
    """
        1 linear about the route
        A more detaild description of the endpoint
        :return: WelcomeSchema().dump(result), 200
        """

    try:

        return get_insurance_company_list(data=request.args.to_dict(), header=request.headers)

    except Exception as error:
        logger.critical(error, exc_info=True)
        return response_message_handler(500)


@information_api.route("/bank", methods=["GET"])
@nocache
@token_required
def bank_info():
    """
        1 linear about the route
        A more detaild description of the endpoint
        :return: WelcomeSchema().dump(result), 200
        """

    try:

        return get_bank_company_list(data=request.args.to_dict(), header=request.headers)

    except Exception as error:
        logger.critical(error, exc_info=True)
        return response_message_handler(500)


@information_api.route("/hospital", methods=["GET"])
@nocache
@token_required
def hospital_info():
    """
        1 linear about the route
        A more detaild description of the endpoint
        :return: WelcomeSchema().dump(result), 200
        """

    try:

        return get_hospital_info(data=request.args.to_dict(), header=request.headers)

    except Exception as error:
        logger.critical(error, exc_info=True)
        return response_message_handler(500)


@information_api.route("/work", methods=["GET"])
@nocache
@token_required
def work_info():
    """
        1 linear about the route
        A more detaild description of the endpoint
        :return: WelcomeSchema().dump(result), 200
        """

    try:

        return get_work_list(data=request.args.to_dict(), header=request.headers)

    except Exception as error:
        logger.critical(error, exc_info=True)
        return response_message_handler(500)
