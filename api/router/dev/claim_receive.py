from flask import Blueprint, request

from api.service.dev.claim_receive import save_claim_receive_info, get_claim_receive_info

from api.util.helper.decorator import token_required, nocache
from api.util.reponse_message import response_message_handler

import logging

logger = logging.getLogger(__name__)

claim_receive_api = Blueprint('dev_claim-receive', __name__)


@claim_receive_api.route("/info", methods=["GET", "POST"])
@nocache
@token_required
def info():

    try:
        if request.method == 'GET':
            return get_claim_receive_info(data=request.args.to_dict(), header=request.headers)
        elif request.method == 'POST':
            return save_claim_receive_info(data=request.form.to_dict(), header=request.headers)

    except Exception as error:
        logger.critical(error, exc_info=True)
        return response_message_handler(500)
