from flask import Blueprint, request

from api.service.v1.insurant import save_insurant_history, get_insurant_history, save_insurant_signature_uploaded, \
    update_insurant_history, get_insurant_work_info, set_insurant_work_info

from api.util.helper.decorator import token_required, nocache
from api.util.reponse_message import response_message_handler

import logging

logger = logging.getLogger(__name__)

insurant_api = Blueprint('insurant', __name__)


@insurant_api.route("/info", methods=["GET", "POST"])
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
            return get_insurant_history(data=request.args.to_dict(), header=request.headers)
        elif request.method == 'POST':
            # request data중에 claim id 파라미터가 들어오는지 확인하고 있으면 갱신 없으면 등록.
            request_data = request.form.to_dict()

            if 'claim_id' not in request_data:
                return save_insurant_history(data=request.form.to_dict(), header=request.headers)
            else:
                return update_insurant_history(data=request.form.to_dict(), header=request.headers)

    except Exception as error:
        logger.critical(error, exc_info=True)
        return response_message_handler(500)


@insurant_api.route("/signature", methods=["POST"])
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
            return save_insurant_signature_uploaded(data=request.form.to_dict(), header=request.headers)

    except Exception as error:
        logger.critical(error, exc_info=True)
        return response_message_handler(500)


@insurant_api.route("/work", methods=["GET", "POST"])
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
            return get_insurant_work_info(data=request.args.to_dict(), header=request.headers)
        elif request.method == 'POST':
            return set_insurant_work_info(data=request.form.to_dict(), header=request.headers)

    except Exception as error:
        logger.critical(error, exc_info=True)
        return response_message_handler(500)
