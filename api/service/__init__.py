import gc
import logging

from flask import Blueprint
from werkzeug.utils import secure_filename

from api.config import file_upload_path
from api.util.reponse_message import response_message_handler

import os

common_api = Blueprint('/', __name__)

logger = logging.getLogger(__name__)


def save_file(request, path):

    logger.info(f'{file_upload_path["URL"]}/{path}')
    logger.info(f'request form  :: {request.files.to_dict()}')

    files = request.files.getlist('file')
    try:
        if len(files) == 0:
            return response_message_handler(400)
        else:
            for file in files:

                """ 파일 이름 조회 시작"""
                logger.info(f' 요청한 파일명 :: {file.filename}')
                """ 파일 이름 조화 끝"""

                filename = secure_filename(file.filename)
                if not os.path.exists(f'{file_upload_path["URL"]}/{path}'):
                    logger.info("폴더 경로가 존재하지 않습니다.")
                    desired_permission = 0o777
                    try:
                        original_umask = os.umask(0)
                        os.makedirs(f'{file_upload_path["URL"]}/{path}', desired_permission)
                    finally:
                        os.umask(original_umask)
                file.save(os.path.join(f'{file_upload_path["URL"]}/{path}', filename))

                if not os.path.exists(os.path.join(f'{file_upload_path["URL"]}/{path}', filename)):
                    return response_message_handler(500)
            return response_message_handler(200)

    except Exception as error:
        logger.error(error, exc_info=True)
        return response_message_handler(500)
    finally:
        gc.collect()
