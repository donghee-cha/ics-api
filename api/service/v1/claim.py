import gc
import json

from api import SessionLocal
from api.config import notification_config, default_host

from api.model.claim_history import ClaimClass
from api.model.insurance import InsuranceClass
from api.model.message_template import MessageTemplateClass
from api.model.notification_send_log import NotificationSendLog
from api.model.partner import PartnerClass

from api.util.plugin.send_notification import SendNotification

from api.util.helper.decorator import parameter_validation
from api.util.helper.time import currentUTCTimestamp, convertTimeToYYYYMMDDWithComma
from api.util.plugin.cipher import AESCipher
from api.util.reponse_message import response_message_handler

import logging

logger = logging.getLogger(__name__)

"""

ics 보험청구 정보 가져오기

"""


@parameter_validation(requires={'claim_id': str})
def get_insurance_claim_info(data, header):
    db = SessionLocal()
    try:
        logger.info("header : {}".format(header))
        logger.info("data : {}".format(data))

        partner_info = db.query(PartnerClass).filter_by(partner_auth_token=header['Auth-Token'])

        if partner_info.count() > 0:
            partner_info = partner_info.first().__dict__
            secret_key = partner_info['partner_secret_key']

            get_claim_info = db.query(ClaimClass).filter_by(claim_id=data['claim_id'])

            if get_claim_info.count() > 0:
                get_claim_info_dict = get_claim_info.first().__dict__

                partner_auth_token = get_claim_info_dict['ec_partner_auth_token']

                auth_token = header['Auth-Token']

                if auth_token == partner_auth_token:
                    cipher = AESCipher()

                    result_claim_info = dict()

                    # 보험사 코드를 보험사 이름으로 변경
                    insurance_code_list = get_claim_info_dict['ec_insurance_code_list']
                    claim_status = get_claim_info_dict['claim_status']
                    # 보험금 청구상태가 0일경우 3으로 변경
                    if get_claim_info_dict['claim_status'] == 0:
                        get_claim_info.first().claim_status = 3
                        claim_status = 3
                        try:
                            db.commit()
                        except Exception as error:
                            logger.critical(error, exc_info=True)
                            db.rollback()
                            return response_message_handler(500)

                    insurance_name_list = ""
                    if insurance_code_list != "":
                        insurance_code_list = insurance_code_list.split(',')

                        for insurance in insurance_code_list:
                            insurance = insurance.strip()
                            get_insurance = db.query(InsuranceClass).filter_by(active=1, ec_code=insurance)
                            if get_insurance.count() > 0:
                                insurance_name_list += get_insurance.first().name + ", "
                    if insurance_name_list != '':
                        result_claim_info['insurance_name_list'] = insurance_name_list[:-2]
                    else:
                        result_claim_info['insurance_name_list'] = ''
                    result_claim_info['claim_type'] = get_claim_info_dict['claim_type']
                    result_claim_info['accident_type'] = get_claim_info_dict['accident_type']
                    result_claim_info['treat_code'] = get_claim_info_dict['treat_code']
                    result_claim_info['insurant_type'] = get_claim_info_dict['insurant_type']
                    result_claim_info['insurant_name'] = get_claim_info_dict['insurant_name']

                    # 주민번호
                    insurant_identify_number_decrypt = cipher.decrypt(
                        secret_key,
                        get_claim_info_dict['insurant_identify_number']
                    )

                    if insurant_identify_number_decrypt != '':
                        result_claim_info['insurant_identify_number'] = get_claim_info_dict['insurant_identify_number']
                    else:
                        result_claim_info['insurant_identify_number'] = ''

                    # 연락처
                    result_claim_info['insurant_cellphone'] = get_claim_info_dict['insurant_cellphone']
                    result_claim_info['insurant_work_code'] = get_claim_info_dict['insurant_work_code']
                    result_claim_info['insurant_work_etc'] = get_claim_info_dict['insurant_work_etc']
                    result_claim_info['insurant_workplace'] = get_claim_info_dict['insurant_workplace']

                    result_claim_info['beneficiary_identify_number'] = ""
                    result_claim_info['beneficiary_cellphone'] = ""
                    result_claim_info['beneficiary_name'] = ""
                    result_claim_info['beneficiary_work_code'] = 0
                    result_claim_info['beneficiary_work_etc'] = ""
                    result_claim_info['beneficiary_workplace'] = ""

                    # 피보험자와 본인이 다를경우 ( 수익자의 이름이 있을경우 )
                    if get_claim_info_dict['beneficiary_name'] != "":

                        result_claim_info['beneficiary_name'] = get_claim_info_dict['beneficiary_name']

                        # 주민번호
                        beneficiary_identify_number_decrypt = cipher.decrypt(
                            secret_key,
                            get_claim_info_dict['beneficiary_identify_number']
                        )

                        if beneficiary_identify_number_decrypt != '':
                            result_claim_info['beneficiary_identify_number'] = get_claim_info_dict[
                                'beneficiary_identify_number']
                        else:
                            result_claim_info['beneficiary_identify_number'] = ''

                        # 연락처
                        result_claim_info['beneficiary_cellphone'] = get_claim_info_dict['beneficiary_cellphone']
                        result_claim_info['beneficiary_work_code'] = get_claim_info_dict['beneficiary_work_code']
                        result_claim_info['beneficiary_work_etc'] = get_claim_info_dict['beneficiary_work_etc']
                        result_claim_info['beneficiary_workplace'] = get_claim_info_dict['beneficiary_workplace']

                    if get_claim_info_dict['bank_code'] != "":
                        result_claim_info['bank_code'] = get_claim_info_dict['bank_code']
                        result_claim_info['bank_account_number'] = get_claim_info_dict['bank_account_number']
                        result_claim_info['bank_account_name'] = get_claim_info_dict['bank_account_name']

                    else:
                        result_claim_info['bank_code'] = ""
                        result_claim_info['bank_account_number'] = ""
                        result_claim_info['bank_account_name'] = ""

                    # 개인 팩스번호등록 조회
                    if get_claim_info_dict['personal_fax_number_list'] != "":
                        result_claim_info['fax_number'] = json.loads(get_claim_info_dict['personal_fax_number_list'])

                    else:
                        result_claim_info['fax_number'] = []

                    # 보험사별 1건 최대 청구 금액 및 콜센터 정보
                    insurance_code_list = get_claim_info_dict['ec_insurance_code_list']
                    insurance_per_max_payment = []
                    insurance_telephone_list = []

                    if insurance_code_list != "":
                        insurance_code_list = insurance_code_list.split(',')

                        for insurance in insurance_code_list:
                            insurance = insurance.strip()

                            insurance_info = dict()
                            insurance_telephone_info = dict()

                            get_insurance = db.query(InsuranceClass).filter_by(active=1, ec_code=insurance)

                            if get_insurance.count() > 0:

                                insurance_info['insurance_code'] = get_insurance.first().ec_code
                                insurance_info['insurance_name'] = get_insurance.first().name
                                payment = str(get_insurance.first().claim_payment_per_count)
                                if payment != "0":
                                    payment_str = "{}만원".format(payment[:-4])
                                    insurance_info['payment'] = payment_str
                                else:
                                    insurance_info['payment'] = "-"

                                insurance_per_max_payment.append(insurance_info)

                                insurance_telephone_info['insurance_code'] = get_insurance.first().ec_code
                                insurance_telephone_info['insurance_name'] = get_insurance.first().name
                                insurance_telephone_info['telephone'] = get_insurance.first().service_telephone
                                insurance_telephone_list.append(insurance_telephone_info)

                    result_claim_info['insurance_per_max_payment'] = insurance_per_max_payment
                    result_claim_info['insurance_telephone'] = insurance_telephone_list

                    # 청구 현황
                    result_claim_info['claim_status'] = claim_status
                    result_claim_info['insurance_send_status'] = get_claim_info_dict['insurance_request_status']
                    result_claim_info['document_status'] = int(get_claim_info_dict['is_uploaded_documentary'])

                    return response_message_handler(200, result_detail=result_claim_info)

                else:
                    return response_message_handler(401)

            else:
                return response_message_handler(401)
        else:
            return response_message_handler(401)

    except Exception as error:
        logger.critical(error, exc_info=True)
        return response_message_handler(500), 500

    finally:
        db.close()
        gc.collect()


"""

ics 보험청구 증빙서류 제출 업로드 여부

"""


@parameter_validation(requires={'claim_id': str, 'is_uploaded': bool})
def save_documentary(data, header):
    db = SessionLocal()

    try:
        logger.info("header : {}".format(header))
        logger.info("data : {}".format(data))

        cipher = AESCipher()
        send_notification = SendNotification(api_url=notification_config['API_URL'],
                                             user_id=notification_config['USER_ID'],
                                             profile=notification_config['PROFILE'])

        secret_key = db.query(PartnerClass).filter_by(
            partner_auth_token=header['Auth-Token']).first().__dict__['partner_secret_key']
        get_claim_info = db.query(ClaimClass).filter_by(claim_id=data['claim_id'])

        if get_claim_info.count() > 0:

            partner_auth_token = get_claim_info.first().ec_partner_auth_token

            auth_token = header['Auth-Token']

            if auth_token == partner_auth_token:

                current_time_stamp = currentUTCTimestamp()
                current_time_stamp_kr = current_time_stamp + (9 * 3600)  # 한국시간

                # 청구접수상태, 접수완료상태면 다음으로 넘어감.
                if eval(data['is_uploaded']):

                    get_claim_info_dict = get_claim_info.first().__dict__

                    get_claim_info.first().is_uploaded_documentary = eval(data['is_uploaded'])
                    get_claim_info.first().insurance_request_date = 0
                    get_claim_info.first().documentary_submit_status = 1
                    get_claim_info.first().update_date = current_time_stamp

                    try:
                        db.commit()

                    except Exception as error:
                        logger.critical(error, exc_info=True)
                        db.rollback()
                        return response_message_handler(500)

                    # 서류 등록시 알림톡 배치 제외
                    try:
                        db.query(NotificationSendLog).filter(
                            NotificationSendLog.claim_id == get_claim_info_dict['claim_id'],
                            NotificationSendLog.is_batch.__eq__(True),
                            NotificationSendLog.type == 5). \
                            update({NotificationSendLog.status: 0})
                        db.commit()
                    except Exception as error:
                        logger.critical(error, exc_info=True)
                        db.rollback()
                        return response_message_handler(500)

                    insurance_code_list = get_claim_info_dict['ec_insurance_code_list'].split(',')

                    # 개인팩스번호가 필요하지 않은 경우 서류첨부만 있는 알림톡 전송 뒤 보험사로 청구서 양식만들고 전송.
                    if get_claim_info_dict['claim_status'] == 1:

                        # 추가서류가 아닌 서류제출 후 보험사로 청구시 알림톡 전송
                        if get_claim_info_dict['documentary_submit_status'] != 2:

                            partner_info = db.query(PartnerClass).filter_by(partner_auth_token=partner_auth_token,
                                                                            active=1)
                            if partner_info.first().hospital_seq > 0:
                                partner_name = partner_info.first().partner_name
                            else:
                                partner_name = ''

                            # 발송할 알림톡 host 가져오기
                            notification_url = partner_info.first().host

                            if notification_url == '':
                                notification_url = default_host

                            # 보험사의 이름 목록들
                            insurance_name_list = ''
                            insurance_need_fax_count = 0
                            for insurance_code in insurance_code_list:
                                get_insurance_info = db.query(InsuranceClass).filter_by(active=1,
                                                                                        ec_code=insurance_code)

                                if get_insurance_info.first():
                                    insurance_name_list += f'{get_insurance_info.first().name},'
                                    if get_insurance_info.first().claim_type == 2:
                                        insurance_need_fax_count += 1

                            if ',' in insurance_name_list:
                                insurance_name_list = insurance_name_list[:-1]

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
                                if beneficiary_cellphone_decrypt != insurant_cellphone_decrypt:
                                    receive_cellphone_list.append(insurant_cellphone_decrypt)

                            # 피보험자가 본인일 경우 피보험자에게만 알림톡 발송
                            else:
                                receive_cellphone_list.append(insurant_cellphone_decrypt)

                            if len(receive_cellphone_list) > 0:

                                get_message_template = db.query(
                                    MessageTemplateClass).filter_by(template_id='ics-006')

                                if get_message_template.count() > 0:
                                    notification_message = get_message_template.first().message

                                    claim_id_reformat = f"{get_claim_info_dict['claim_id'][0:6]}-" \
                                                        f"{get_claim_info_dict['claim_id'][6:]}"
                                    notification_message = notification_message.replace(
                                        '#{NAME}', get_claim_info_dict['insurant_name'])
                                    notification_message = notification_message.replace(
                                        '#{CLAIMID}', claim_id_reformat)
                                    notification_message = notification_message.replace(
                                        '#{COMPANY}', insurance_name_list)
                                    notification_message = notification_message.replace(
                                        '#{PARTNER}', partner_name)
                                    notification_message = notification_message.replace(
                                        '#{REGDATE}', convertTimeToYYYYMMDDWithComma(current_time_stamp_kr))

                                    notification_message = notification_message.replace(
                                        "#{STATUS_URL}", notification_config['BUTTON_URL'].format(
                                            notification_url, get_claim_info_dict['claim_id']))

                                    for receive_cellphone in receive_cellphone_list:

                                        notification_message_json = json.loads(notification_message, strict=False)

                                        notification_response = send_notification.send_notification(
                                            data=notification_message_json[0],
                                            profile_key=notification_config['PROFILE'],
                                            receive_number=f"{notification_config['ITU']}{receive_cellphone[1:]}",
                                            reservation_date=''
                                        )
                                        # 알림톡 로그쌓기
                                        new_notification_send_log = NotificationSendLog(
                                            claim_id=get_claim_info_dict['claim_id'],
                                            type=0,
                                            message_template_seq=get_message_template.first().seq,
                                            send_message=json.dumps(notification_message_json[0],
                                                                    ensure_ascii=False),
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
                                else:
                                    logger.info("청구완료 알림톡 템플릿이 존재하지 않습니다.")
                            else:
                                logger.info("보낼 알림톡 번호가 존재하지 않습니다")
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
