import gc
import json

from api import SessionLocal
from api.config import notification_message_template, notification_config

from api.model.message_template import MessageTemplateClass
from api.model.notification_send_log import NotificationSendLog
from api.model.partner import PartnerClass
from api.util.helper.decorator import parameter_validation
from api.util.helper.time import convertTimeToYYYYMMDDList, currentKorTimestamp
from api.util.plugin.cipher import AESCipher
from api.util.plugin.send_notification import SendNotification
from api.util.reponse_message import response_message_handler

import logging

logger = logging.getLogger(__name__)


@parameter_validation(requires={'cellphone': str})
def save_send_notification(data, header):
    auth_token = header['Auth-Token']
    encrypt_cellphone = data['cellphone']

    template_id = ''

    db = SessionLocal()
    cipher = AESCipher()
    _send_notification = SendNotification(api_url=notification_config['API_URL'],
                                          user_id=notification_config['USER_ID'],
                                          profile=notification_config['PROFILE'])
    current_time_stamp = currentKorTimestamp()
    current_date_obj = convertTimeToYYYYMMDDList(current_time_stamp)

    try:

        if 'template_id' in data:
            template_id = data['template_id']

        partner_info = db.query(PartnerClass).filter_by(partner_auth_token=auth_token)

        if template_id != '':
            get_message_template = db.query(
                MessageTemplateClass).filter_by(template_id=template_id)
        else:
            get_message_template = db.query(
                MessageTemplateClass).filter_by(template_id=notification_message_template['LIFEPLANET'])

        if partner_info.count() > 0:

            if get_message_template.count() > 0:

                partner_info = partner_info.first().__dict__
                secret_key = partner_info['partner_secret_key']
                decrypt_cellphone = cipher.decrypt(secret_key, encrypt_cellphone)

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

        else:
            return response_message_handler(401)

    except Exception as error:
        logger.critical(error, exc_info=True)
        return response_message_handler(500)
    finally:
        db.close()
        gc.collect()
