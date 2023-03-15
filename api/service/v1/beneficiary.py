import gc

from api import SessionLocal

from api.model.claim_history import ClaimClass
from api.model.partner import PartnerClass
from api.model.plugin_config import PluginConfigClass
from api.util.helper.decorator import parameter_validation
from api.util.helper.time import currentUTCTimestamp
from api.util.plugin.cipher import AESCipher
from api.util.reponse_message import response_message_handler

import logging

logger = logging.getLogger(__name__)

"""

ics 이용내역 기록 등록하고 접수번호 발행해주기

"""


@parameter_validation(requires={'claim_id': str, 'beneficiary_name': str, 'beneficiary_identify_number': str,
                                'beneficiary_cellphone': str, 'beneficiary_relationship_type': int})
def save_beneficiary_history(data, header):
    db = SessionLocal()
    try:
        logger.debug("header : {}".format(header))
        logger.debug("data : {}".format(data))

        get_claim_info = db.query(ClaimClass).filter_by(claim_id=data['claim_id'])

        if get_claim_info.count() > 0:

            partner_auth_token = get_claim_info.first().ec_partner_auth_token

            auth_token = header['Auth-Token']

            if auth_token == partner_auth_token:

                current_time_stamp = currentUTCTimestamp()

                get_claim_info.first().beneficiary_name = data['beneficiary_name']
                get_claim_info.first().beneficiary_identify_number = data['beneficiary_identify_number']
                get_claim_info.first().beneficiary_cellphone = data['beneficiary_cellphone']
                get_claim_info.first().beneficiary_relationship_type = data['beneficiary_relationship_type']
                get_claim_info.first().update_date = current_time_stamp

                try:
                    db.commit()
                except Exception as error:
                    logger.critical(error, exc_info=True)
                    db.rollback()
                    return response_message_handler(500)

                return response_message_handler(200)

            else:
                return response_message_handler(401)
        else:
            return response_message_handler(401)

    except Exception as error:
        logger.critical(error, exc_info=True)
        return response_message_handler(500)
    finally:
        db.close()
        gc.collect()


"""

ics 이용내역 가져오기

"""


@parameter_validation(requires={'claim_id': str})
def get_beneficiary_history(data, header):
    db = SessionLocal()
    try:

        logger.debug("header : {}".format(header))
        logger.debug("data : {}".format(data))

        get_claim_info = db.query(ClaimClass).filter_by(claim_id=data['claim_id'])
        partner_info = db.query(PartnerClass).filter_by(partner_auth_token=header['Auth-Token'])

        if get_claim_info.count() > 0:

            if partner_info.count() > 0:

                partner_info = partner_info.first().__dict__
                secret_key = partner_info['partner_secret_key']

                get_claim_info_dict = get_claim_info.first().__dict__

                partner_auth_token = get_claim_info_dict['ec_partner_auth_token']

                auth_token = header['Auth-Token']

                if auth_token == partner_auth_token:

                    cipher = AESCipher()

                    beneficiary_info = dict()

                    if get_claim_info_dict['beneficiary_name'] == "" and \
                            get_claim_info_dict['beneficiary_identify_number'] == "" and \
                            get_claim_info_dict['beneficiary_cellphone'] == "":

                        return response_message_handler(204)

                    else:

                        beneficiary_info['beneficiary_name'] = get_claim_info_dict['beneficiary_name']

                        # 주민번호
                        beneficiary_identify_number_decrypt = cipher.decrypt(secret_key,
                                                                             get_claim_info_dict[
                                                                                 'beneficiary_identify_number']
                                                                             )

                        if beneficiary_identify_number_decrypt != '':

                            beneficiary_info['beneficiary_identify_number'] = get_claim_info_dict[
                                                                                 'beneficiary_identify_number']
                        else:
                            beneficiary_info['beneficiary_identify_number'] = ''

                        # 연락처
                        beneficiary_info['beneficiary_cellphone'] = get_claim_info_dict['beneficiary_cellphone']
                        beneficiary_info[
                            'beneficiary_relationship_type'] = get_claim_info_dict['beneficiary_relationship_type']
                        if get_claim_info_dict['is_uploaded_beneficiary_signature'] == 1:

                            # 파트너사별 버킷 정보 가져오기
                            plugin_information = db.query(PluginConfigClass).filter_by(
                                seq=partner_info['plugin_config_seq'])

                            if plugin_information.count() > 0:
                                plugin_information = plugin_information.first().__dict__
                                s3_information = dict()
                                s3_information['S3_KEY'] = plugin_information['s3_access_key']
                                s3_information['S3_SECRET_KEY'] = plugin_information['s3_secret_key']
                                s3_information['REGION'] = plugin_information['s3_region']
                                s3_information['BUCKET'] = plugin_information['s3_bucket']
                                s3_information['DOCUMENT_DIR'] = 'document'
                                s3_information['SIGNATURE_DIR'] = 'signature'
                                s3_information['INSURANT_SIGNATURE_FILE'] = "insurant_signature.png"
                                s3_information['BENEFICIARY_SIGNATURE_FILE'] = "beneficiary_signature.png"

                                beneficiary_info['beneficiary_signature_file'] = \
                                    f"https://{s3_information['BUCKET']}.s3.{s3_information['REGION']}." \
                                    f"amazonaws.com/{s3_information['SIGNATURE_DIR']}/{get_claim_info_dict['claim_id']}/" \
                                    f"{s3_information['BENEFICIARY_SIGNATURE_FILE']}"
                            else:
                                beneficiary_info['beneficiary_signature_file'] = ''

                        else:
                            beneficiary_info['beneficiary_signature_file'] = ''

                        return response_message_handler(200, result_detail=beneficiary_info)

                else:
                    return response_message_handler(401)
            else:
                return response_message_handler(401)
        else:
            return response_message_handler(401)

    except Exception as error:
        logger.critical(error, exc_info=True)
        return response_message_handler(500)

    finally:
        db.close()
        gc.collect()


"""
수익자 서명파일 업로드 완료 여부 갱신
"""


@parameter_validation(requires={'claim_id': str, 'is_uploaded': bool})
def save_beneficiary_signature_uploaded(data, header):
    db = SessionLocal()
    try:

        logger.debug("header : {}".format(header))
        logger.debug("data : {}".format(data))

        get_claim_info = db.query(ClaimClass).filter_by(claim_id=data['claim_id'])

        if get_claim_info.count() > 0:

            partner_auth_token = get_claim_info.first().ec_partner_auth_token

            auth_token = header['Auth-Token']

            if auth_token == partner_auth_token:
                current_time_stamp = currentUTCTimestamp()
                get_claim_info.first().is_uploaded_beneficiary_signature = bool(int(data['is_uploaded']))
                get_claim_info.first().update_date = current_time_stamp

                try:
                    db.commit()
                except Exception as error:
                    logger.critical(error, exc_info=True)
                    db.rollback()
                    return response_message_handler(500)

                return response_message_handler(200)
            else:
                return response_message_handler(401)
        else:
            return response_message_handler(401)

    except Exception as error:
        logger.critical(error, exc_info=True)
        return response_message_handler(500)

    finally:
        db.close()
        gc.collect()



"""

피보험자 Job 가져오기

"""


@parameter_validation(requires={'claim_id': str})
def get_beneficiary_work_info(data, header):
    db = SessionLocal()

    auth_token = header['Auth-Token']
    claim_id = data['claim_id']

    response = ''
    try:

        partner_info = db.query(PartnerClass).filter_by(partner_auth_token=auth_token)
        get_claim_info = db.query(ClaimClass).filter_by(
            claim_id=claim_id, active=1).order_by(ClaimClass.create_date.desc())

        if partner_info.count() > 0:

            if get_claim_info.count() > 0:

                get_claim_info = get_claim_info.first()

                if auth_token == get_claim_info.ec_partner_auth_token:

                    result = dict(work_code=get_claim_info.beneficiary_work_code,
                                  work_etc=get_claim_info.beneficiary_work_etc,
                                  workplace=get_claim_info.beneficiary_workplace)

                    response = response_message_handler(200, result_detail=result)
                    del result

                else:
                    response = response_message_handler(401)
            else:
                response = response_message_handler(401)
        else:
            response = response_message_handler(401)

    except Exception as error:
        logger.critical(error, exc_info=True)
        response = response_message_handler(500)
    finally:
        gc.collect()
        return response


"""

수익자 직장명/하시는일 등록 및 수정

"""


@parameter_validation(requires={'claim_id': str, 'work_code': int})
def set_beneficiary_work_info(data, header):
    db = SessionLocal()

    auth_token = header['Auth-Token']
    claim_id = data['claim_id']
    work_code = data['work_code']
    work_etc = data['work_etc'] if 'work_etc' in data and data['work_etc'] else ''
    workplace = data['workplace'] if 'workplace' in data and data['workplace'] else ''

    response = ''
    try:
        # 직업코드가 기타가 아닌경우 etc로 들어오는지 확인
        if int(work_code) == 999 and work_etc == '':
            response = response_message_handler(400)
        else:
            get_claim_info = db.query(ClaimClass).filter_by(
                claim_id=claim_id, active=1).order_by(ClaimClass.create_date.desc())

            if get_claim_info.count() > 0:
                get_claim_info = get_claim_info.first()
                if auth_token == get_claim_info.ec_partner_auth_token:

                    try:
                        current_time_stamp = currentUTCTimestamp()
                        get_claim_info.beneficiary_work_code = work_code
                        get_claim_info.beneficiary_work_etc = work_etc
                        get_claim_info.beneficiary_workplace = workplace
                        get_claim_info.update_date = current_time_stamp

                        del current_time_stamp
                        del get_claim_info

                        db.commit()
                        response = response_message_handler(200)

                    except Exception as error:
                        logger.critical(error, exc_info=True)
                        db.rollback()
                        response = response_message_handler(500)

                else:
                    logger.info(f'<<<<<<청구 이용자의 Auth-Token이 다릅니다>>>>>>')
                    response = response_message_handler(401)
            else:
                response = response_message_handler(204)

    except Exception as error:
        logger.critical(error, exc_info=True)
        response = response_message_handler(500)
    finally:
        db.close()
        gc.collect()
        return response