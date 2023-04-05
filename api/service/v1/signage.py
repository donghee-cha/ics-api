import datetime
import gc
import os
from os.path import exists, basename
from shutil import copyfile

from api import SessionLocal
from api.config import contents_path, api_url

from api.model.partner import PartnerClass
from api.model.signage_publish import SignagePublishClass
from api.model.signage_storage import SignageStorageClass

from api.util.reponse_message import response_message_handler

import zipfile
import logging

logger = logging.getLogger(__name__)

"""

고객사 사이니지 정보 가져오기

"""


def get_signage_info(data, header):
    db = SessionLocal()
    try:

        logger.debug("header : {}".format(header))
        logger.debug("data : {}".format(data))

        auth_token = header['Auth-Token']
        result = dict()
        signage_list = []

        partner_info = db.query(PartnerClass).filter_by(partner_auth_token=auth_token, active=1)

        if partner_info.count() > 0:
            partner_info = partner_info.first().__dict__

            signage_publish_info = db.query(SignagePublishClass).filter_by(
                partner_code=partner_info['partner_code']).order_by(SignagePublishClass.signage_publish_number.desc())

            if signage_publish_info.count() > 0:
                logger.info(f"압축파일 정보 : {signage_publish_info.first().file_name}")
                # 압축파일이 만들어졌을 경우
                if signage_publish_info.first().file_name != '':

                    signage_publish_info = signage_publish_info.first().__dict__
                    file_name = signage_publish_info["file_name"]
                    signage_file_path = f"{partner_info['partner_code']}/signage"

                    signage_absolute_path = f'{contents_path}/{signage_file_path}/{file_name}'

                    if exists(signage_absolute_path):

                        signage_storage_seq_list = signage_publish_info['signage_storage_seq_list']

                        if signage_storage_seq_list != '':
                            if ',' in signage_storage_seq_list:
                                signage_seq_list = signage_storage_seq_list.split(',')
                            else:
                                signage_seq_list = [signage_storage_seq_list]
                        # 반복문 돌면서 사이니지 정보 가져오기
                        for signage_seq in signage_seq_list:
                            signage_info = db.query(SignageStorageClass).filter_by(seq=signage_seq)

                            signage_info = signage_info.first().__dict__
                            signage_list.append(dict(content_type=signage_info['content_type'],
                                                     content_file_name=signage_info['file_name'],
                                                     content_output_time=signage_info['output_time'],
                                                     content_close_date=signage_info['close_date']))
                            del signage_info

                        result['signage_list'] = signage_list
                        result['signage_file_url'] = f"{api_url}/contents/{signage_file_path}/{file_name}"
                        result['signage_publish_number'] = signage_publish_info['signage_publish_number']

                        del signage_list
                        del signage_seq_list

                        return response_message_handler(200, result_detail=result)

                    else:
                        logger.info(f"{signage_absolute_path} 파일이 존재하지 않습니다.")
                        return response_message_handler(204)

                # 압축파일이 만들어지지 않았을 경우 새로만듬
                else:

                    zip_file_name = f'{int(datetime.datetime.utcnow().timestamp())}.zip'
                    common_signage_file_path = f"common/signage"
                    signage_file_path = f"{partner_info['partner_code']}/signage"

                    common_signage_absolute_path = f'{contents_path}/{common_signage_file_path}'
                    signage_absolute_path = f'{contents_path}/{signage_file_path}'
                    zip_absolute_path = f'{contents_path}/{signage_file_path}/{zip_file_name}'

                    # 파일 리스트 가져오기
                    signage_seq_list = []
                    signage_name_list = []

                    signage_storage_seq_list = signage_publish_info.first().signage_storage_seq_list

                    if ',' in signage_storage_seq_list:
                        signage_seq_list = signage_storage_seq_list.split(',')

                    else:
                        signage_seq_list.append(signage_storage_seq_list)

                    # 게시 버전의 폴더가 존재하지 않으면 생성함.
                    if not os.path.exists(signage_absolute_path):
                        os.umask(0)
                        os.makedirs(signage_absolute_path, mode=0o777)

                    idx = 1
                    for signage_seq in signage_seq_list:

                        signage_info = db.query(SignageStorageClass).filter_by(seq=signage_seq)

                        if signage_info.count() > 0:
                            signage_storage_info = signage_info.first().__dict__
                            file_name = f'{int(datetime.datetime.utcnow().timestamp())}_{idx}.' \
                                        f'{signage_storage_info["file_name"].split(".")[1]}'

                            if signage_storage_info['origin_seq'] > 0 and signage_storage_info['status'] == 0:
                                if os.path.exists(
                                        f'{common_signage_absolute_path}/{signage_storage_info["file_name"]}'):
                                    copyfile(f'{common_signage_absolute_path}/{signage_storage_info["file_name"]}',
                                             f'{signage_absolute_path}/{file_name}')

                            else:

                                if os.path.exists(f'{signage_absolute_path}/{signage_storage_info["file_name"]}'):
                                    logger.info(f'복사하는 파일명 : {signage_storage_info["file_name"]}')
                                    copyfile(f'{signage_absolute_path}/{signage_storage_info["file_name"]}',
                                             f'{signage_absolute_path}/{file_name}')

                            signage_info.first().status = 1
                            signage_info.first().file_name = file_name
                            signage_info.first().update_date = datetime.datetime.utcnow().timestamp()
                            idx += 1
                            try:
                                db.commit()
                            except Exception as error:
                                logger.critical(error, exc_info=True)
                                db.rollback()
                                return response_message_handler(500)

                            signage_name_list.append(file_name)

                            logger.info(signage_name_list)

                            signage_list.append(dict(content_type=signage_storage_info['content_type'],
                                                     content_file_name=file_name,
                                                     content_output_time=signage_storage_info['output_time'],
                                                     content_close_date=signage_storage_info['close_date']))
                            del signage_storage_info

                    with zipfile.ZipFile(zip_absolute_path, 'w') as zip_file:
                        for signage_name in signage_name_list:
                            logger.info(f'{contents_path}/{signage_file_path}/{signage_name}')
                            if os.path.isfile(f'{contents_path}/{signage_file_path}/{signage_name}'):
                                filePath = os.path.join(f'{contents_path}/{signage_file_path}', signage_name)
                                logger.info(filePath)
                                zip_file.write(filePath, basename(filePath), compress_type=zipfile.ZIP_DEFLATED)

                    # 파일명 변경
                    signage_publish_info.first().file_name = zip_file_name
                    signage_publish_info.first().update_date = datetime.datetime.utcnow().timestamp()

                    try:
                        db.commit()

                        result['signage_list'] = signage_list
                        result['signage_file_url'] = f"{api_url}/contents/{signage_file_path}/{zip_file_name}"
                        result['signage_publish_number'] = signage_publish_info.first().signage_publish_number

                        del signage_list
                        del signage_seq_list

                        return response_message_handler(200, result_detail=result)

                    except Exception as error:
                        logger.critical(error, exc_info=True)
                        db.rollback()
                        return response_message_handler(500)

            else:
                logger.info("게시된 정보가 없습니다")
                return response_message_handler(204)

        else:
            logger.info("파트너사 정보가 없습니다")
            return response_message_handler(401)

    except Exception as error:
        logger.critical(error, exc_info=True)
        return response_message_handler(500)

    finally:
        db.close()
        gc.collect()
