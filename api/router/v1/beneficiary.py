
from flask import Blueprint, request

from api.service.v1.beneficiary import (save_beneficiary_history, get_beneficiary_history,
                                        save_beneficiary_signature_uploaded, get_beneficiary_work_info,
                                        set_beneficiary_work_info)

from api.util.helper.decorator import token_required, nocache
from api.util.reponse_message import response_message_handler

import logging

logger = logging.getLogger(__name__)

beneficiary_api = Blueprint('beneficiary', __name__)


@beneficiary_api.route("/info", methods=["GET", "POST"])
@nocache
@token_required
def info():

    try:
        if request.method == 'GET':
            return get_beneficiary_history(data=request.args.to_dict(), header=request.headers)
        elif request.method == 'POST':
            return save_beneficiary_history(data=request.form.to_dict(), header=request.headers)

    except Exception as error:
        logger.critical(error, exc_info=True)
        return response_message_handler(400)


@beneficiary_api.route("/signature", methods=["POST"])
@nocache
@token_required
def signature():
    """
        1 linear about the route
        A more detaild description of the endpoint
        :return: WelcomeSchema().dump(result), 200
        """

    try:
        if request.method == 'POST':
            return save_beneficiary_signature_uploaded(data=request.form.to_dict(), header=request.headers)

    except Exception as error:
        logger.critical(error, exc_info=True)
        return response_message_handler(400)



@beneficiary_api.route("/work", methods=["GET", "POST"])
@nocache
@token_required
def work():
    """
        1 linear about the route
        A more detaild description of the endpoint
        :return: WelcomeSchema().dump(result), 200
        """

    try:
        if request.method == 'GET':
            return get_beneficiary_work_info(data=request.args.to_dict(), header=request.headers)
        elif request.method == 'POST':
            return set_beneficiary_work_info(data=request.form.to_dict(), header=request.headers)

    except Exception as error:
        logger.critical(error, exc_info=True)
        return response_message_handler(400)