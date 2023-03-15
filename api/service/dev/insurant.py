import gc

from api import SessionLocal

from api.model.claim_history_dev import ClaimClass
from api.model.partner import PartnerClass
from api.model.plugin_config import PluginConfigClass
from api.model.terms import TermsClass
from api.model.work import WorkClass
from api.util.helper.decorator import parameter_validation
from api.util.helper.time import currentUTCTimestamp, convertTimeToYYYYMMDD
from api.util.plugin.cipher import AESCipher
from api.util.reponse_message import response_message_handler

import random, logging

logger = logging.getLogger(__name__)

"""

ics 피보험자 청구신청 등록하고 접수번호 발행해주기


"""


@parameter_validation(requires={'device': str, 'terms_list': str, 'insurant_name': str, 'insurant_identify_number': str,
                                'insurant_cellphone': str, 'is_need_protect': bool, 'partner_code': str,
                                'insurant_type': int
                                })
def save_insurant_history(data, header):
    db = SessionLocal()

    try:

        logger.info("header : {}".format(header))
        logger.info("data : {}".format(data))

        partner_code = data['partner_code']

        auth_token = header['Auth-Token']

        partner_info = db.query(PartnerClass).filter_by(partner_auth_token=auth_token)

        if partner_info.count() > 0:

            # 정보 이용동의 파싱
            get_terms_list = data['terms_list']
            set_terms_list = []

            # 제 3자 개인정보이용동의 ( 선택 ), 마케팅 정보 동의 (선택)
            get_third_party_agree = ''
            get_marketing_agree = ''

            if get_terms_list != "":
                get_terms_arr = get_terms_list.split(',')

                if len(get_terms_arr) > 0:
                    for terms in get_terms_arr:
                        terms_info = dict()
                        terms_parse = terms.split('-')
                        terms_info['seq'] = terms_parse[0].replace(' ', '')
                        terms_info['response'] = terms_parse[1]
                        set_terms_list.append(terms_info)

                        # 이용동의 정보에서 type 가져오기
                        get_terms_info = db.query(TermsClass).filter_by(seq=terms_info['seq'])
                        if get_terms_info.count() > 0:
                            if get_terms_info.first().agree_type == 'third':
                                get_third_party_agree = terms_info['response']

                            elif get_terms_info.first().agree_type == 'marketing':
                                get_marketing_agree = terms_info['response']

            current_time_stamp = currentUTCTimestamp()
            current_date = convertTimeToYYYYMMDD(current_time_stamp)
            current_date_yymmdd = current_date.replace('-', '')[2:]

            # 사용자 정보를 가져와서 마지막 접수번호에서 + 1 해주기
            last_claim_info = db.query(ClaimClass).filter(ClaimClass.claim_id.ilike(f"{current_date_yymmdd}%"))

            # 청구번호 발행 (현재 날짜 + timestamp)
            claim_id = current_date.replace('-', '')[2:] + str(random.randrange(0, 9999)) + str(
                last_claim_info.count() + 1)

            new_history = ClaimClass(claim_id=claim_id,
                                     device=data['device'],
                                     terms_description=str(set_terms_list),
                                     terms_third_party_agree=get_third_party_agree,
                                     terms_marketing_agree=get_marketing_agree,
                                     ec_partner_auth_token=auth_token,
                                     ec_partner_code=partner_code,
                                     insurant_name=data['insurant_name'],
                                     insurant_identify_number=data['insurant_identify_number'],
                                     insurant_cellphone=data['insurant_cellphone'],
                                     is_need_protect=bool(int(data['is_need_protect'])),
                                     create_date=current_time_stamp,
                                     insurant_type=int(data['insurant_type'])
                                     )
            try:
                db.add(new_history)
                db.commit()
            except Exception as error:
                logger.critical(error, exc_info=True)
                db.rollback()
                return response_message_handler(500)

            return response_message_handler(200, result_detail={"claim_id": claim_id})
        else:
            return response_message_handler(401)

    except Exception as error:
        logger.critical(error, exc_info=True)
        return response_message_handler(500)
    finally:
        db.close()
        gc.collect()


"""

ICS 피보험자 청구신청 갱신하기

"""


@parameter_validation(requires={'insurant_name': str, 'insurant_identify_number': str, 'insurant_cellphone': str,
                                'insurant_type': int, 'is_need_protect': int})
def update_insurant_history(data, header):
    db = SessionLocal()
    try:

        logger.info("header : {}".format(header))
        logger.info("data : {}".format(data))

        if data['claim_id'] != "":

            get_claim_info = db.query(ClaimClass).filter_by(claim_id=data['claim_id'])

            if get_claim_info.count() > 0:

                partner_auth_token = get_claim_info.first().ec_partner_auth_token

                auth_token = header['Auth-Token']

                if auth_token == partner_auth_token:

                    get_claim_info.first().insurant_type = int(data['insurant_type'])
                    get_claim_info.first().insurant_name = data['insurant_name']
                    get_claim_info.first().insurant_identify_number = data['insurant_identify_number']
                    get_claim_info.first().insurant_cellphone = data['insurant_cellphone']
                    get_claim_info.first().is_need_protect = bool(int(data['is_need_protect']))

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
def get_insurant_history(data, header):
    db = SessionLocal()

    try:

        logger.info("header : {}".format(header))
        logger.info("data : {}".format(data))

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

                    claim_info = dict()

                    claim_info['insurant_name'] = get_claim_info_dict['insurant_name']

                    insurant_identify_number_decrypt = cipher.decrypt(secret_key,
                                                                      get_claim_info_dict['insurant_identify_number']
                                                                      )

                    if insurant_identify_number_decrypt != '':
                        claim_info['insurant_identify_number'] = get_claim_info_dict['insurant_identify_number']
                    else:
                        claim_info['insurant_identify_number'] = ''

                    claim_info['insurant_cellphone'] = get_claim_info_dict['insurant_cellphone']
                    claim_info['is_need_protect'] = bool(int(get_claim_info_dict['is_need_protect']))
                    claim_info['insurant_type'] = int(get_claim_info_dict['insurant_type'])

                    if get_claim_info.first().is_uploaded_insurant_signature == 1:

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

                            claim_info['insurant_signature_file'] = \
                                f"https://{s3_information['BUCKET']}.s3.{s3_information['REGION']}." \
                                f"amazonaws.com/{s3_information['SIGNATURE_DIR']}/" \
                                f"{get_claim_info_dict['claim_id']}/{s3_information['INSURANT_SIGNATURE_FILE']}"
                        else:
                            claim_info['insurant_signature_file'] = ""
                    else:
                        claim_info['insurant_signature_file'] = ""

                    return response_message_handler(200, result_detail=claim_info)

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
피보험자 서명파일 업로드 완료 여부 갱신
"""


@parameter_validation(requires={'claim_id': str, 'is_uploaded': bool})
def save_insurant_signature_uploaded(data, header):
    db = SessionLocal()
    try:

        logger.info("header : {}".format(header))
        logger.info("data : {}".format(data))

        get_claim_info = db.query(ClaimClass).filter_by(claim_id=data['claim_id'])

        if get_claim_info.count() > 0:

            partner_auth_token = get_claim_info.first().ec_partner_auth_token

            auth_token = header['Auth-Token']

            if auth_token == partner_auth_token:
                current_time_stamp = currentUTCTimestamp()
                get_claim_info.first().is_uploaded_insurant_signature = bool(int(data['is_uploaded']))
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
def get_insurant_work_info(data, header):
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

                    result = dict(work_code=get_claim_info.insurant_work_code,
                                  work_etc=get_claim_info.insurant_work_etc,
                                  workplace=get_claim_info.insurant_workplace)

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

피보험자 직장명/하시는일 등록 및 수정

"""


@parameter_validation(requires={'claim_id': str, 'work_code': int})
def set_insurant_work_info(data, header):
    db = SessionLocal()

    auth_token = header['Auth-Token']
    claim_id = data['claim_id']
    work_code = data['work_code']
    work_etc = data['work_etc'] if 'work_etc' in data and data['work_etc'] else ''
    workplace = data['workplace'] if 'work_etc' in data and data['workplace'] else ''

    response = ''
    get_work_info = ''
    try:

        # 직업코드가 기타가 아닌경우 etc로 들어오는지 확인
        if int(work_code) != 999 and work_etc != '':
            response = response_message_handler(400)
        else:

            get_claim_info = db.query(ClaimClass).filter_by(
                claim_id=claim_id, active=1).order_by(ClaimClass.create_date.desc())

            if get_claim_info.count() > 0:
                get_claim_info = get_claim_info.first()
                if auth_token == get_claim_info.ec_partner_auth_token:

                    try:
                        current_time_stamp = currentUTCTimestamp()
                        get_claim_info.insurant_work_code = work_code
                        get_claim_info.insurant_work_etc = work_etc
                        get_claim_info.insurant_workplace = workplace
                        get_claim_info.update_date = current_time_stamp

                        del current_time_stamp
                        del get_claim_info

                        db.commit()
                        response = response_message_handler(200)

                    except Exception as error:
                        logger.critical(error, exc_info=True)
                        db.rollback()
                        response = response_message_handler(500)
                    finally:
                        db.close()
                else:
                    response = response_message_handler(401)
            else:
                response = response_message_handler(204)

    except Exception as error:
        logger.critical(error, exc_info=True)
        response = response_message_handler(500)
    finally:
        gc.collect()
        return response
