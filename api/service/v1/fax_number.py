import ast
import gc
import json

from api import SessionLocal
from api.config import notification_config, default_host

from api.model.claim_history import ClaimClass
from api.model.insurance import InsuranceClass
from api.model.message_template import MessageTemplateClass
from api.model.notification_send_log import NotificationSendLog
from api.model.partner import PartnerClass
from api.util.plugin.cipher import AESCipher
from api.util.plugin.send_notification import SendNotification
from api.util.helper.decorator import parameter_validation
from api.util.helper.time import currentUTCTimestamp, convertTimeToYYYYMMDDWithComma
from api.util.reponse_message import response_message_handler

import logging

logger = logging.getLogger(__name__)

"""

ics 개인팩스번호 등록하기

"""


@parameter_validation(requires={'claim_id': str, 'fax_number': str})
def save_fax_number(data, header):
    db = SessionLocal()

    try:

        cipher = AESCipher()
        send_notification = SendNotification(api_url=notification_config['API_URL'],
                                             user_id=notification_config['USER_ID'],
                                             profile=notification_config['PROFILE'])

        logger.debug("header : {}".format(header))
        logger.debug("data : {}".format(data))

        secret_key = db.query(PartnerClass).filter_by(
            partner_auth_token=header['Auth-Token']).first().__dict__['partner_secret_key']
        get_claim_info = db.query(ClaimClass).filter_by(claim_id=data['claim_id'])

        if get_claim_info.count() > 0:

            partner_auth_token = get_claim_info.first().ec_partner_auth_token
            auth_token = header['Auth-Token']
            is_fax_number_success = 1

            if auth_token == partner_auth_token:

                if get_claim_info.first().claim_status != 0:

                    current_time_stamp = currentUTCTimestamp()
                    current_time_stamp_kr = current_time_stamp + (9 * 3600)  # 한국시간

                    fax_number_strip = data['fax_number'].replace("\n", "")
                    fax_number_strip = fax_number_strip.replace(" ", "")
                    register_insurance_list = ast.literal_eval(fax_number_strip)

                    if get_claim_info.first().ec_insurance_code_list != "":

                        ec_insurance_code_list = get_claim_info.first().ec_insurance_code_list.split(',')

                        # 피보험자가 신청한 보험사중 개인 팩스번호가 필요한 보험사면 개인 팩스번호를 등록해야만 보험금을 청구할 수 있음.
                        for insurance_code in ec_insurance_code_list:

                            insurance_info = db.query(InsuranceClass).filter_by(active=1, ec_code=insurance_code)

                            if insurance_info.first() is not None and insurance_info.first().claim_type == 2:
                                is_register = 0

                                for register_insurance in register_insurance_list:
                                    if insurance_code == register_insurance['insurance_code'] and \
                                            register_insurance['fax_number'] != '':
                                        is_register = 1
                                if is_register == 0:
                                    is_fax_number_success = 0

                    if is_fax_number_success == 0:
                        get_claim_info.first().claim_status = 2
                    else:
                        get_claim_info.first().claim_status = 1

                    get_claim_info.first().personal_fax_number_list = json.dumps(
                        register_insurance_list)

                    get_claim_info.first().claim_date = current_time_stamp
                    get_claim_info.first().update_date = current_time_stamp

                    try:
                        db.commit()

                    except Exception as error:
                        logger.critical(error, exc_info=True)
                        db.rollback()
                        return response_message_handler(500)

                    # 개인 팩스번호가 모두 등록이 되었을 경우 + 접수가 완료 되었을 경우 알림톡을 발송한다.
                    if is_fax_number_success == 1:

                        get_claim_info = db.query(ClaimClass).filter_by(claim_id=data['claim_id'])

                        # 개인 팩스번호 알림톡 상태 갱신 ( 발송을 안하는 상태로 변경 )
                        try:
                            db.query(NotificationSendLog).filter(NotificationSendLog.claim_id == data['claim_id'],
                                                                 NotificationSendLog.is_batch.__eq__(True),
                                                                 NotificationSendLog.type == 4). \
                                update({NotificationSendLog.status: 0})
                            db.commit()
                        except Exception as error:
                            logger.critical(error, exc_info=True)
                            db.rollback()
                            return response_message_handler(500)

                        # 청구접수상태, 접수완료상태면 보험사 청구서류 발송.
                        if get_claim_info.first().is_uploaded_documentary == 1:

                            get_claim_info_dict = get_claim_info.first().__dict__

                            insurance_code_list = get_claim_info_dict['ec_insurance_code_list'].split(',')

                            partner_info = db.query(PartnerClass).filter_by(partner_auth_token=partner_auth_token,
                                                                            active=1)

                            # 추가서류가 아닌 서류제출 후 보험사로 청구시 알림톡 전송
                            if get_claim_info_dict['documentary_submit_status'] != 2 and \
                                    get_claim_info_dict['is_uploaded_documentary'] == 1:

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

                                            notification_message_json = json.loads(notification_message,
                                                                                   strict=False)

                                            notification_response = send_notification.send_notification(
                                                data=notification_message_json[0],
                                                profile_key=notification_config['PROFILE'],
                                                receive_number=f"{notification_config['ITU']}{receive_cellphone[1:]}",
                                                reservation_date=''
                                            )
                                            # 알림톡 로그쌓기:q!
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
                    return response_message_handler(400)
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


@parameter_validation(requires={'claim_id': str})
def get_fax_number(data, header):
    db = SessionLocal()

    try:

        logger.debug("header : {}".format(header))
        logger.debug("data : {}".format(data))

        result_detail = {'insurant_fax_number': ''}

        get_claim_info = db.query(ClaimClass).filter_by(claim_id=data['claim_id'])

        if get_claim_info.count() > 0:

            partner_auth_token = get_claim_info.first().ec_partner_auth_token

            auth_token = header['Auth-Token']

            if auth_token == partner_auth_token:

                if get_claim_info.first().ec_insurance_code_list != "":

                    insurance_code_list = get_claim_info.first().ec_insurance_code_list.split(',')
                    set_insurance_code_arr = []
                    insurant_fax_number_list = []
                    if get_claim_info.first().personal_fax_number_list != "":
                        insurant_fax_number_list = json.loads(get_claim_info.first().personal_fax_number_list)

                    for index, insurance_code in enumerate(insurance_code_list):
                        insurance_code = insurance_code.replace(" ", "")
                        insurance_code_dict = dict()
                        insurance_info = db.query(InsuranceClass).filter_by(active=1, ec_code=insurance_code)

                        if insurance_info.first():
                            # 개인 팩스번호가 필요한 보험사의 경우
                            if insurance_info.first().claim_type == 2:
                                insurance_code_dict['insurance_code'] = insurance_code
                                insurance_code_dict['telephone'] = insurance_info.first().service_telephone
                                insurance_code_dict['fax_number'] = ''

                                # 피보험자가 개인팩스번호를 등록했으면 보여줌
                                for insurant_fax_number in insurant_fax_number_list:

                                    if insurance_code == insurant_fax_number['insurance_code']:
                                        insurance_code_dict['fax_number'] = insurant_fax_number['fax_number']

                            if insurance_code_dict:
                                set_insurance_code_arr.append(insurance_code_dict)

                    result_detail['insurant_fax_number'] = set_insurance_code_arr

                    return response_message_handler(200, result_detail=result_detail)

                else:
                    return response_message_handler(204)

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
