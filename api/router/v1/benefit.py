from flask import Blueprint, request

from api.util.helper.decorator import nocache, token_required
from api.util.reponse_message import response_message_handler

from api.service.v1.benefit import get_benefit_info, set_benefit_participate
import logging

logger = logging.getLogger(__name__)

benefit_api = Blueprint('benefit', __name__)


@benefit_api.route("/info", methods=["GET"])
@nocache
@token_required
def info():
    try:
        return get_benefit_info(data=request.args.to_dict(), header=request.headers)
    except Exception as error:
        logger.error(error, exc_info=True)
        return response_message_handler(500)


@benefit_api.route("/participate", methods=["POST"])
@nocache
@token_required
def participate():
    try:
        return set_benefit_participate(data=request.form.to_dict(), header=request.headers)
    except Exception as error:
        logger.error(error, exc_info=True)
        return response_message_handler(500)
