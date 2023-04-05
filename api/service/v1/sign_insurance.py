import gc
import json

from api import SessionLocal
from api.config import notification_message_template, notification_config, default_hospital_code, \
    default_hospital_sido_code, default_hospital_sigungu_code, master_key
from api.model.district_sido import DistrictSidoClass
from api.model.district_sigungu import DistrictSigunguClass
from api.model.hospital import HospitalClass
from api.model.kiosk_service import KioskServiceClass

from api.model.message_template import MessageTemplateClass
from api.model.notification_send_log import NotificationSendLog
from api.model.partner import PartnerClass
from api.model.sign_insurance_find_application import SignInsuranceFindApplicantClass
from api.model.sign_insurance_history import SignInsuranceHistoryClass
from api.util.helper.decorator import parameter_validation
from api.util.helper.regex import is_valid_cellphone
from api.util.helper.time import convertTimeToYYYYMMDDList, currentKorTimestamp, currentUTCTimestamp
from api.util.plugin.cipher import AESCipher
from api.util.plugin.send_notification import SendNotification
from api.util.reponse_message import response_message_handler

import logging

logger = logging.getLogger(__name__)


@parameter_validation(requires={'device': str, 'name': str, 'cellphone': str})
def save_sign_insurance_find(data, header):
    auth_token = header['Auth-Token']
    encrypt_cellphone = data['cellphone']
    encrypt_name = data['name']

    template_id = ''
    sido_code = default_hospital_sido_code
    sigungu_code = default_hospital_sigungu_code

    db = SessionLocal()
    cipher = AESCipher()
    _send_notification = SendNotification(api_url=notification_config['API_URL'],
                                          user_id=notification_config['USER_ID'],
                                          profile=notification_config['PROFILE'])
    current_time_stamp = currentKorTimestamp()
    current_date_obj = convertTimeToYYYYMMDDList(current_time_stamp)

    try:

        partner_info = db.query(PartnerClass).filter_by(partner_auth_token=auth_token)

        if template_id != '':
            get_message_template = db.query(
                MessageTemplateClass).filter_by(template_id=template_id)
        else:
            get_message_template = db.query(
                MessageTemplateClass).filter_by(template_id=notification_message_template['LIFEPLANET'])

        if partner_info.count() > 0:

            get_partner_info = partner_info.first().__dict__

            secret_key = get_partner_info['partner_secret_key']
            decrypt_cellphone = cipher.decrypt(secret_key, encrypt_cellphone)

            if is_valid_cellphone(decrypt_cellphone):

                # 신청 정보 저장
                if get_partner_info['hospital_seq'] > 0:
                    hospital_info = db.query(HospitalClass).filter_by(
                        seq=get_partner_info['hospital_seq'], active=1)

                    if hospital_info.count() == 0:
                        hospital_info = db.query(HospitalClass).filter_by(code=default_hospital_code)

                    get_hospital_info = hospital_info.first().__dict__
                    hospital_name = get_hospital_info['name']
                    hospital_code = get_hospital_info['code']

                    # 병원코드가 기본코드가 아닐경우에만 시도, 시군구 코드를 가져옴
                    if hospital_code != default_hospital_code:
                        sido_code = int(hospital_code[0:2])
                        sigungu_code = int(hospital_code[0:6])

                    sido_info = db.query(DistrictSidoClass).filter_by(code=sido_code, active=1)
                    sigungu_info = db.query(DistrictSigunguClass).filter_by(code=sigungu_code, active=1)

                    get_sido_info = sido_info.first().__dict__
                    get_sigungu_info = sigungu_info.first().__dict__

                    new_insurance_find_applicant = SignInsuranceFindApplicantClass(
                        device_code=data['device'],
                        device_use_date=current_time_stamp,
                        applicant_id='EVCARE',
                        applicant_cellphone=encrypt_cellphone,
                        applicant_name=encrypt_name,
                        hospital_name=hospital_name,
                        hospital_code=hospital_code,
                        district_sido_code=get_sido_info['code'],
                        district_sido_name=get_sido_info['name'],
                        district_sigungu_code=get_sigungu_info['code'],
                        district_sigungu_name=get_sigungu_info['name'],
                        create_date=current_time_stamp
                    )
                    try:
                        db.add(new_insurance_find_applicant)
                        db.commit()

                        if get_message_template.count() > 0:

                            notification_message = get_message_template.first().message
                            notification_message = notification_message.replace('#{신청년도}', current_date_obj['year'])
                            notification_message = notification_message.replace('#{신청월}', current_date_obj['month'])
                            notification_message = notification_message.replace('#{신청일}', current_date_obj['day'])

                            notification_message_json = json.loads(notification_message, strict=False)

                            notification_response = _send_notification.send_notification(
                                data=notification_message_json[0],
                                profile_key=notification_config['PROFILE'],
                                receive_number=f"{notification_config['ITU']}{decrypt_cellphone[1:]}",
                                reservation_date=''
                            )
                            # 알림톡 로그쌓기
                            new_notification_send_log = NotificationSendLog(
                                claim_id='',
                                type=0,
                                message_template_seq=get_message_template.first().seq,
                                send_message=json.dumps(notification_message_json[0], ensure_ascii=False),
                                send_date=current_time_stamp,
                                is_send_success=notification_response,
                                create_date=current_time_stamp
                            )
                            try:
                                db.add(new_notification_send_log)
                                db.commit()
                            except Exception as error:
                                logger.critical(error, exc_info=True)
                                db.rollback()

                            if notification_response == 1:
                                return response_message_handler(200)
                            else:
                                return response_message_handler(500)
                        else:
                            logger.info("청구완료 알림톡 템플릿이 존재하지 않습니다.")
                            return response_message_handler(500)

                    except Exception as error:
                        logger.critical(error, exc_info=True)
                        db.rollback()
                        return response_message_handler(500)
                else:
                    logger.info(" 파트너사의 병원정보가 존재하지 않습니다 ")
                    return response_message_handler(204)
            else:
                logger.info("휴대폰 정보가 올바르지 않습니다.")
                return response_message_handler(400)
        else:
            return response_message_handler(401)

    except Exception as error:
        logger.critical(error, exc_info=True)
        return response_message_handler(500)
    finally:
        db.close()
        gc.collect()


@parameter_validation(requires={'device_code': str, 'name': str, 'birthday': str, 'cellphone': str,
                                'insurance_information': str})
def save_sign_insurance_info(data, header):

    auth_token = header['Auth-Token']
    device = data['device_code']
    encrypt_name = data['name']
    encrypt_birthday = data['birthday']
    encrypt_cellphone = data['cellphone']
    insurance_information = data['insurance_information']

    db = SessionLocal()
    current_time_stamp = currentUTCTimestamp()

    try:

        partner_info = db.query(PartnerClass).filter_by(partner_auth_token=auth_token,
                                                        active=1)

        if partner_info.count() > 0:
            # 디바이스 조회
            kiosk_service_info = db.query(KioskServiceClass).filter_by(device_code=device, signage_flag=False)

            if kiosk_service_info.count() > 0:

                new_sign_insurance_history = SignInsuranceHistoryClass(
                    device_code=device,
                    name=encrypt_name,
                    cellphone=encrypt_cellphone,
                    birthday=encrypt_birthday,
                    insurance_information=insurance_information,
                    create_date=current_time_stamp
                )
                try:
                    db.add(new_sign_insurance_history)
                    db.commit()
                    return response_message_handler(200,
                                                    result_detail={"sign_insurance_id": new_sign_insurance_history.seq})

                except Exception as error:
                    logger.critical(error, exc_info=True)
                    return response_message_handler(500)
            else:
                logger.info("키오스크 정보가 존재하지 않습니다.")
                return response_message_handler(204)
        else:
            return response_message_handler(401)

    except Exception as error:
        logger.critical(error, exc_info=True)
        return response_message_handler(500)
    finally:
        db.close()
        gc.collect()


@parameter_validation(requires={'sign_insurance_id': int})
def update_sign_insurance_result(data, header):

    auth_token = header['Auth-Token']
    sign_insurance_id = data['sign_insurance_id']

    db = SessionLocal()
    current_time_stamp = currentUTCTimestamp()
    insurance_document_request_agree = '' if 'insurance_document_request_agree' not in data or \
                                             data['insurance_document_request_agree'] == '' else \
        data['insurance_document_request_agree']
    insurance_coverage_case = '' if 'insurance_coverage_case' not in data or data['insurance_coverage_case'] == '' \
        else data['insurance_coverage_case']

    try:

        partner_info = db.query(PartnerClass).filter_by(partner_auth_token=auth_token,
                                                        active=1)

        if partner_info.count() > 0:
            if insurance_document_request_agree != '' or insurance_coverage_case != '':

                # 보험 가입내역 조회
                sign_insurance_info = db.query(SignInsuranceHistoryClass).filter_by(seq=sign_insurance_id, active=1)

                if sign_insurance_info.count() > 0:

                    try:
                        sign_insurance_info.first().insurance_document_request_agree = insurance_document_request_agree
                        sign_insurance_info.first().insurance_coverage_case = insurance_coverage_case
                        sign_insurance_info.first().update_date = current_time_stamp

                        try:
                            db.commit()
                        except Exception as error:
                            logger.critical(error, exc_info=True)
                            db.rollback()
                            return response_message_handler(500)

                        return response_message_handler(200)

                    except Exception as error:
                        logger.critical(error, exc_info=True)
                        return response_message_handler(500)

                else:
                    logger.info("보험 가입내역 조회 정보가 존재하지 않습니다.")
                    return response_message_handler(204)
            else:
                logger.info("보험서류요청 여부 혹은 보험보장케이스를 입력해주세요")
                return response_message_handler(400)
        else:
            return response_message_handler(401)

    except Exception as error:
        logger.critical(error, exc_info=True)
        return response_message_handler(500)
    finally:
        db.close()
        gc.collect()
