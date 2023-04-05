from flask import Blueprint, request

from api.service.dev.setting import get_available_install_info, set_install_kiosk_info

from api.util.helper.decorator import token_required, nocache
from api.util.reponse_message import response_message_handler

import logging

logger = logging.getLogger(__name__)

setting_api = Blueprint('dev_setting', __name__)


@setting_api.route("/info", methods=["GET", "POST"])
@nocache
@token_required
def info():

    try:
        if request.method == 'GET':
            return get_available_install_info(data=request.args.to_dict(), header=request.headers)
        elif request.method == "POST":
            return set_install_kiosk_info(data=request.form.to_dict(), header=request.headers)

    except Exception as error:
        logger.critical(error, exc_info=True)
        return response_message_handler(500)

