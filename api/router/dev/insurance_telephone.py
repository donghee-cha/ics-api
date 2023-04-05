from flask import Blueprint, request

from api.service.dev.insurance_telephone import get_insurance_telephone_info

from api.util.helper.decorator import token_required, nocache
from api.util.reponse_message import response_message_handler

import logging

logger = logging.getLogger(__name__)

insurance_telephone_api = Blueprint('dev_insurance-telephone', __name__)


@insurance_telephone_api.route("/info", methods=["GET"])
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
            return get_insurance_telephone_info(data=request.args.to_dict(), header=request.headers)

    except Exception as error:
        logger.critical(error, exc_info=True)
        return response_message_handler(500)
