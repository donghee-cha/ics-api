import gc
import json
from datetime import timezone

from api import SessionLocal
from api.config import notification_config, default_host

from api.model.claim_history import ClaimClass
from api.model.insurance import InsuranceClass
from api.model.message_template import MessageTemplateClass
from api.model.notification_send_log import NotificationSendLog
from api.model.partner import PartnerClass
from api.util.helper.decorator import parameter_validation
from api.util.helper.time import convertTimeToYYYYMMDDWithComma, currentUTCTimestamp, convertTimeToDateTime, \
    plusDaysTimestamp
from api.util.plugin.cipher import AESCipher
from api.util.plugin.send_notification import SendNotification
from api.util.reponse_message import response_message_handler

import logging

logger = logging.getLogger(__name__)

"""

ics 청구 진행상태 조회하기

"""


@parameter_validation(requires={'claim_id': str})
def get_claim_status_info(data, header):
    db = SessionLocal()
    try:

        logger.debug("header : {}".format(header))
        logger.debug("data : {}".format(data))

        get_claim_info = db.query(ClaimClass).filter_by(claim_id=data['claim_id'])

        if get_claim_info.count() > 0:

            result_claim_info = dict()
            result_claim_info['claim_status'] = get_claim_info.first().claim_status
            result_claim_info['insurance_send_status'] = get_claim_info.first().insurance_request_status
            result_claim_info['document_status'] = int(get_claim_info.first().is_uploaded_documentary)

            return response_message_handler(200, result_detail=result_claim_info)

        else:
            return response_message_handler(204)

    except Exception as error:
        logger.critical(error, exc_info=True)
        return response_message_handler(500)

    finally:
        db.close()
        gc.collect()


@parameter_validation(requires={'claim_id': str})
def post_claim_status_info(data, header):
    db = SessionLocal()
    try:

        cipher = AESCipher()
        send_notification = SendNotification(api_url=notification_config['API_URL'],
                                             user_id=notification_config['USER_ID'],
                                             profile=notification_config['PROFILE'])

        logger.debug("header : {}".format(header))
        logger.debug("data : {}".format(data))

        get_claim_info = db.query(ClaimClass).filter_by(claim_id=data['claim_id'])

        if get_claim_info.count() > 0:

            get_claim_info_dict = get_claim_info.first().__dict__
            partner_auth_token = get_claim_info_dict['ec_partner_auth_token']

            auth_token = header['Auth-Token']

            if auth_token == partner_auth_token:

                current_time_stamp = currentUTCTimestamp()
                current_time_stamp_kr = current_time_stamp + (9 * 3600)

                # 파트너사 조회
                partner_info = db.query(PartnerClass).filter_by(partner_auth_token=partner_auth_token)

                if partner_info.count() > 0:

                    partner_info = partner_info.first().__dict__

                    partner_name = partner_info['partner_name']
                    secret_key = partner_info['partner_secret_key']
                    # 발송할 알림톡 host 가져오기
                    notification_url = partner_info['host']

                    if notification_url == '':
                        notification_url = default_host

                    # 청구할 보험사 이름 목록
                    insurance_name_list = ''
                    # 필요한 개인 팩스번호 수
                    insurance_need_fax_count = 0
                    # 개인팩스번호 필요 여부
                    is_need_personal_fax_number = 0

                    # 개인팩스번호 필요한 보험사 선택시 개인 팩스번호 등록 대기로 변경
                    insurance_code_list = get_claim_info_dict['ec_insurance_code_list'].split(',')

                    for insurance in insurance_code_list:

                        get_insurance = db.query(InsuranceClass).filter_by(active=1, ec_code=insurance)

                        if get_insurance.count() > 0:
                            insurance_name_list += f'{get_insurance.first().name},'
                            if get_insurance.first().claim_type == 2:
                                is_need_personal_fax_number = 1
                            if get_insurance.first().claim_type == 2:
                                insurance_need_fax_count += 1

                    if ',' in insurance_name_list:
                        insurance_name_list = insurance_name_list[:-1]

                    # 청구상태가 접수등록대기 (3 또는 0) 일때 변경됨
                    if get_claim_info_dict['claim_status'] == 3 or get_claim_info_dict['claim_status'] == 0:

                        # 알림톡 수신자 셋팅
                        receive_cellphone_list = []
                        insurant_cellphone_decrypt = cipher.decrypt(
                            secret_key,
                            get_claim_info_dict['insurant_cellphone']
                        )
                        # 피보험자가 본인이 아닐 경우 수익자와 피보험자 둘다 알림톡 발송
                        if get_claim_info_dict['insurant_type'] == 1:
                            beneficiary_cellphone_decrypt = cipher.decrypt(
                                secret_key,
                                get_claim_info_dict['beneficiary_cellphone']
                            )
                            receive_cellphone_list.append(beneficiary_cellphone_decrypt)

                            receive_batch_cellphone = beneficiary_cellphone_decrypt
                            if beneficiary_cellphone_decrypt != insurant_cellphone_decrypt:
                                receive_cellphone_list.append(insurant_cellphone_decrypt)

                        # 피보험자가 본인일 경우 피보험자에게만 알림톡 발송
                        else:
                            receive_cellphone_list.append(insurant_cellphone_decrypt)
                            receive_batch_cellphone = insurant_cellphone_decrypt

                        # 개인 팩스번호가 필요할때 알림톡 (청구접수 완료 팩스형 + 3일치 개인 팩스번호 등록 요청 오후 3시 및 서류접수 오전 8시반 알림톡 나감)
                        if is_need_personal_fax_number == 1:

                            get_claim_info.first().claim_status = 2

                            try:
                                db.commit()
                            except Exception as error:
                                logger.critical(error, exc_info=True)
                                db.rollback()
                                return response_message_handler(500)

                            new_notification_send_logs = []

                            # 3일치 배치 데이터 ( 서류 접수 type=5 + 개인 팩스번호 등록요청 type=4)
                            # 파트너사별로 알림톡 전송 타입이 다를 수가 있음. (20 : 기본, 10: 신청접수만 나감, 90: 다나감, 99: 알림톡 취소)
                            if partner_info['send_notification_type'] == 90:

                                document_notification_time = current_time_stamp + 3600
                                fax_notification_time = current_time_stamp + 1800

                                get_message_template_fax = db.query(
                                    MessageTemplateClass).filter_by(template_id='ics-002')
                                get_message_template_document = db.query(
                                    MessageTemplateClass).filter_by(template_id='ics-001')

                                claim_id_reformat = f"{get_claim_info_dict['claim_id'][0:6]}-" \
                                                    f"{get_claim_info_dict['claim_id'][6:]}"

                                if get_message_template_fax.count() > 0:
                                    notification_message_fax = get_message_template_fax.first().message

                                    notification_message_fax = notification_message_fax.replace(
                                        "#{NAME}", get_claim_info_dict['insurant_name'])

                                    notification_message_fax = notification_message_fax.replace(
                                        "#{CLAIMID}", claim_id_reformat)
                                    notification_message_fax = notification_message_fax.replace(
                                        "{COMPANY}", insurance_name_list)
                                    notification_message_fax = notification_message_fax.replace(
                                        "{FAX_URL}", notification_config['BUTTON_URL'].format(
                                            notification_url, get_claim_info_dict['claim_id']))

                                    notification_message_fax_json = json.loads(notification_message_fax, strict=False)

                                else:
                                    logger.info("개인팩스번호 알림톡이 존재하지 않습니다")

                                if get_message_template_document.count() > 0:
                                    notification_message_document = get_message_template_document.first().message

                                    notification_message_document = notification_message_document.replace(
                                        "#{NAME}", get_claim_info_dict['insurant_name'])

                                    notification_message_document = notification_message_document.replace(
                                        "#{CLAIMID}", claim_id_reformat)
                                    notification_message_document = notification_message_document.replace(
                                        "{REGDATE}", convertTimeToYYYYMMDDWithComma(current_time_stamp_kr))
                                    notification_message_document = notification_message_document.replace(
                                        "{DOCUMENT_URL}", notification_config['BUTTON_URL'].format(
                                            get_claim_info_dict['claim_id']))

                                    notification_message_document_json = json.loads(notification_message_document,
                                                                                    strict=False)
                                else:
                                    logger.info("서류등록요청 알림톡이 존재하지 않습니다")
                                if len(notification_message_fax_json) > 0 and \
                                        len(notification_message_document_json) > 0:

                                    send_message_fax = send_notification.get_notification_message(
                                        data=notification_message_fax_json[0],
                                        profile_key=notification_config['PROFILE'],
                                        receive_number=f"{notification_config['ITU']}{receive_batch_cellphone[1:]}",
                                        reservation_date='')

                                    send_message_document = send_notification.get_notification_message(
                                        data=notification_message_document_json[0],
                                        profile_key=notification_config['PROFILE'],
                                        receive_number=f"{notification_config['ITU']}{receive_batch_cellphone[1:]}",
                                        reservation_date='')

                                    for i in range(3):
                                        new_notification_send_logs.append(
                                            NotificationSendLog(
                                                is_batch=bool(1),
                                                claim_id=get_claim_info_dict['claim_id'],
                                                type=0,
                                                message_template_seq=get_message_template_fax.first().seq,
                                                send_message=json.dumps(send_message_fax, ensure_ascii=False),
                                                send_reservation_date=fax_notification_time,
                                                create_date=current_time_stamp
                                            )
                                        )
                                        new_notification_send_logs.append(
                                            NotificationSendLog(
                                                is_batch=bool(1),
                                                claim_id=get_claim_info_dict['claim_id'],
                                                type=0,
                                                message_template_seq=get_message_template_document.first().seq,
                                                send_message=json.dumps(send_message_document, ensure_ascii=False),
                                                send_reservation_date=document_notification_time,
                                                create_date=current_time_stamp
                                            )
                                        )

                                        # 개인 팩스번호 : 다음날 오전 10시, 서류등록 : 다음날 오전 11시
                                        document_notification_time = plusDaysTimestamp(
                                            convertTimeToDateTime(document_notification_time),
                                            1).replace(hour=2, minute=0, second=0, microsecond=0,
                                                       tzinfo=timezone.utc).timestamp()
                                        fax_notification_time = plusDaysTimestamp(
                                            convertTimeToDateTime(fax_notification_time),
                                            1).replace(hour=1, minute=0, second=0, microsecond=0,
                                                       tzinfo=timezone.utc).timestamp()

                                    try:
                                        db.bulk_save_objects(
                                            new_notification_send_logs
                                        )
                                        db.commit()
                                    except Exception as error:
                                        logger.critical(error, exc_info=True)
                                        db.rollback()

                                else:
                                    logger.info("서류등록 알림톡 혹은 개인팩스번호등록 알림톡이 존재하지 않습니다.")

                            else:
                                logger.info(f"{partner_info['partner_code']} 의 알림톡 타입은 기본입니다")

                        else:
                            get_claim_info.first().claim_status = 1
                            get_claim_info.first().claim_date = current_time_stamp
                            get_claim_info.first().update_date = current_time_stamp

                            try:
                                db.commit()
                            except Exception as error:
                                logger.critical(error, exc_info=True)
                                db.rollback()
                                return response_message_handler(500)

                            new_notification_send_logs = []

                            if partner_info['send_notification_type'] == 90:

                                get_message_template_document = db.query(
                                    MessageTemplateClass).filter_by(template_id='ics-001')

                                # 3일치 배치 데이터 ( 서류 접수 요청)
                                document_notification_time = current_time_stamp + 3600
                                claim_id_reformat = f"{get_claim_info_dict['claim_id'][0:6]}-" \
                                                    f"{get_claim_info_dict['claim_id'][6:]}"

                                if get_message_template_document.count() > 0:
                                    notification_message_document = get_message_template_document.first().message

                                    notification_message_document = notification_message_document.replace("#{NAME}",
                                                                                                          get_claim_info_dict[
                                                                                                              'insurant_name'])

                                    notification_message_document = notification_message_document.replace(
                                        "#{CLAIMID}",
                                        claim_id_reformat)
                                    notification_message_document = notification_message_document.replace(
                                        "{REGDATE}",
                                        convertTimeToYYYYMMDDWithComma(
                                            current_time_stamp_kr))
                                    notification_message_document = notification_message_document.replace(
                                        "{DOCUMENT_URL}",
                                        notification_config[
                                            'BUTTON_URL'].
                                            format(get_claim_info_dict[
                                                       'claim_id']))

                                    notification_message_document_json = json.loads(notification_message_document,
                                                                                    strict=False)

                                    send_message_document = send_notification.get_notification_message(
                                        data=notification_message_document_json[0],
                                        profile_key=notification_config['PROFILE'],
                                        receive_number=f"{notification_config['ITU']}{receive_batch_cellphone[1:]}",
                                        reservation_date='')
                                    for i in range(3):
                                        new_notification_send_logs.append(
                                            NotificationSendLog(
                                                is_batch=bool(1),
                                                claim_id=get_claim_info_dict['claim_id'],
                                                type=0,
                                                message_template_seq=get_message_template_document.first().seq,
                                                send_message=json.dumps(send_message_document, ensure_ascii=False),
                                                send_reservation_date=document_notification_time,
                                                create_date=current_time_stamp
                                            )
                                        )
                                        # 개인 팩스번호 : 다음날 오전 10시, 서류등록 : 다음날 오전 11시
                                        document_notification_time = plusDaysTimestamp(
                                            convertTimeToDateTime(document_notification_time),
                                            1).replace(hour=2, minute=0, second=0, microsecond=0,
                                                       tzinfo=timezone.utc).timestamp()

                                    try:
                                        db.bulk_save_objects(
                                            new_notification_send_logs
                                        )
                                        db.commit()
                                    except Exception as error:
                                        logger.critical(error, exc_info=True)
                                        db.rollback()
                                else:
                                    logger.info("서류등록요청 알림톡 템플릿이 존재하지 않습니다.")
                            else:
                                logger.info(f"{partner_info['partner_code']} 의 알림톡 타입은 기본입니다")

                        return response_message_handler(200)
                    else:
                        return response_message_handler(400)
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
