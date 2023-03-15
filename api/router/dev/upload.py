from flask import Blueprint, request

from api.service.dev.upload import upload_document

from api.util.helper.decorator import token_required, nocache
from api.util.reponse_message import response_message_handler

import logging

logger = logging.getLogger(__name__)

upload_api = Blueprint('dev_upload', __name__)


@upload_api.route("/document", methods=["POST"])
@nocache
@token_required
def document():
    """
        1 linear about the route
        A more detaild description of the endpoint
        :return: WelcomeSchema().dump(result), 200
        """
    try:
        return upload_document(data=request.form.to_dict(), header=request.headers)
    except Exception as error:
        logger.critical(error, exc_info=True)
        return response_message_handler(400)

