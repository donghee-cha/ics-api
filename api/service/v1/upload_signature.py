import gc
import os

from botocore.exceptions import ClientError

from api import SessionLocal
from api.config import file_upload_path, s3_config

from api.model.claim_history import ClaimClass
from api.model.partner import PartnerClass
from api.util.helper.decorator import parameter_validation
from api.util.helper.time import currentUTCTimestamp
from api.util.reponse_message import response_message_handler

import logging
import boto3

logger = logging.getLogger(__name__)


@parameter_validation(requires={'upload_target': str, 'claim_id': str, 'upload_flag': bool})
def upload_signature_insurant(data, header):
    db = SessionLocal()

    try:

        logger.debug("header : {}".format(header))
        logger.debug("data : {}".format(data))

        auth_token = header['Auth-Token']

        partner_info = db.query(PartnerClass).filter_by(partner_auth_token=auth_token)

        if partner_info.count() > 0:

            get_claim_info = db.query(ClaimClass).filter_by(claim_id=data['claim_id'])

            """ 1. upload target path 확인해서 s3이면 업로드, 아니면, 등록완료로만 확인"""
            if get_claim_info.count() > 0:
                if data['upload_target'] == 'S3':

                    get_claim_info.first().is_uploaded_insurant_signature = eval(data['upload_flag'])
                    get_claim_info.first().update_date = currentUTCTimestamp()

                    try:
                        db.commit()
                    except Exception as error:
                        logger.critical(error, exc_info=True)
                        db.rollback()
                        return response_message_handler(500)

                    return response_message_handler(200)
                    """ 2. s3 이면 디렉토리 안에 파일이 있는지 확인"""
                elif data['upload_target'] == 'WS':
                    insurant_signature_file_path = f'{file_upload_path["URL"]}/{file_upload_path["BUCKET"]}' \
                                                   f'/signature/{data["claim_id"]}/insurant_signature.png'
                    if not os.path.exists(insurant_signature_file_path):
                        return response_message_handler(204, result_message='피보험자 서명파일이 없습니다.')
                    else:
                        s3_client = boto3.client('s3',
                                                 aws_access_key_id=s3_config['AWS_ACCESS_KEY'],
                                                 aws_secret_access_key=s3_config['AWS_SECRET_KEY'],
                                                 region_name=s3_config['REGION'])
                        file = insurant_signature_file_path
                        key_path = f'signature/{data["claim_id"]}/insurant_signature.png'
                        try:
                            s3_client.upload_file(file, file_upload_path["BUCKET"], key_path)
                            """ 올려놨던 파일 삭제 """
                            try:
                                os.remove(insurant_signature_file_path)
                                logger.info(f'{insurant_signature_file_path} 삭제!!!')
                            except Exception as error:
                                logger.error(error, exc_info=True)

                        except ClientError as error:
                            logging.error(error, exc_info=True)
                            return response_message_handler(500, result_message='s3업로드 중 오류가 발행하였습니다')

                        get_claim_info.first().is_uploaded_insurant_signature = eval(data['upload_flag'])
                        get_claim_info.first().update_date = currentUTCTimestamp()

                        try:
                            db.commit()
                        except Exception as error:
                            logger.critical(error, exc_info=True)
                            db.rollback()
                            return response_message_handler(500)

                        return response_message_handler(200)

                else:
                    return response_message_handler(204, result_message='업로드 대상지점이 없습니다.')

            else:
                return response_message_handler(204, result_message='청구정보가 없습니다.')

        else:
            return response_message_handler(401)

    except Exception as error:
        logger.critical(error, exc_info=True)
        return response_message_handler(500)
    finally:
        db.close()
        gc.collect()


@parameter_validation(requires={'upload_target': str, 'claim_id': str, 'upload_flag': bool})
def upload_signature_beneficiary(data, header):
    db = SessionLocal()

    try:

        logger.debug("header : {}".format(header))
        logger.debug("data : {}".format(data))

        auth_token = header['Auth-Token']

        partner_info = db.query(PartnerClass).filter_by(partner_auth_token=auth_token)

        if partner_info.count() > 0:

            get_claim_info = db.query(ClaimClass).filter_by(claim_id=data['claim_id'])

            """ 1. upload target path 확인해서 s3이면 업로드, 아니면, 등록완료로만 확인"""
            if get_claim_info.count() > 0:
                if data['upload_target'] == 'S3':

                    get_claim_info.first().is_uploaded_beneficiary_signature = eval(data['upload_flag'])
                    get_claim_info.first().update_date = currentUTCTimestamp()

                    try:
                        db.commit()
                    except Exception as error:
                        logger.critical(error, exc_info=True)
                        db.rollback()
                        return response_message_handler(500)

                    return response_message_handler(200)
                    """ 2. s3 이면 디렉토리 안에 파일이 있는지 확인"""
                elif data['upload_target'] == 'WS':
                    beneficiary_signature_file_path = f'{file_upload_path["URL"]}/{file_upload_path["BUCKET"]}' \
                                                   f'/signature/{data["claim_id"]}/beneficiary_signature.png'
                    if not os.path.exists(beneficiary_signature_file_path):
                        return response_message_handler(204, result_message='피보험자 서명파일이 없습니다.')
                    else:
                        s3_client = boto3.client('s3',
                                                 aws_access_key_id=s3_config['AWS_ACCESS_KEY'],
                                                 aws_secret_access_key=s3_config['AWS_SECRET_KEY'],
                                                 region_name=s3_config['REGION'])
                        file = beneficiary_signature_file_path
                        key_path = f'signature/{data["claim_id"]}/beneficiary_signature.png'
                        try:
                            s3_client.upload_file(file, s3_config['BUCKET_NAME'], key_path)
                            """ 올려놨던 파일 삭제 """
                            try:
                                os.remove(beneficiary_signature_file_path)
                                logger.info(f'{beneficiary_signature_file_path} 삭제!!!')
                            except Exception as error:
                                logger.error(error, exc_info=True)
                        except ClientError as error:
                            logging.error(error, exc_info=True)
                            return response_message_handler(500, result_message='s3업로드 중 오류가 발행하였습니다')

                        get_claim_info.first().is_uploaded_beneficiary_signature = eval(data['upload_flag'])
                        get_claim_info.first().update_date = currentUTCTimestamp()

                        try:
                            db.commit()
                        except Exception as error:
                            logger.critical(error, exc_info=True)
                            db.rollback()
                            return response_message_handler(500)

                        return response_message_handler(200)

                else:
                    return response_message_handler(204, result_message='업로드 대상지점이 없습니다.')

            else:
                return response_message_handler(204, result_message='청구정보가 없습니다.')

        else:
            return response_message_handler(401)

    except Exception as error:
        logger.critical(error, exc_info=True)
        return response_message_handler(500)
    finally:
        db.close()
        gc.collect()
