from flask import Blueprint, request

from api.service.v1.setting_signage import set_install_signage_info

from api.util.helper.decorator import token_required, nocache
from api.util.reponse_message import response_message_handler

import logging

logger = logging.getLogger(__name__)

setting_signage_api = Blueprint('setting-signage', __name__)


@setting_signage_api.route("/info", methods=["POST"])
@nocache
@token_required
def info():
    try:
        return set_install_signage_info(data=request.form.to_dict(), header=request.headers)

    except Exception as error:
        logger.critical(error, exc_info=True)
        return response_message_handler(400)
