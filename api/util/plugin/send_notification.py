import json

from api.config import notification_config

from urllib import request

import logging

logger = logging.getLogger(__name__)

"""
비즈엠 알림톡
"""


class SendNotification:

    def __init__(self, api_url, user_id, profile):
        self.api_url = api_url
        self.user_id = user_id
        self.profile = profile

    # 알림톡 전송
    def send_notification(self, data, profile_key, receive_number, reservation_date):

        try:

            is_success = 0

            logger.debug(data)
            data['message_type'] = data['type']
            del data['type']

            data['tmplId'] = data['template_id']
            del data['template_id']

            data['msg'] = data['message']
            del data['message']

            if reservation_date == '':
                data['reserveDt'] = "00000000000000"
            else:
                data['reserveDt'] = reservation_date

            data['phn'] = receive_number
            data['profile'] = profile_key

            message = [data]

            url = f'{self.api_url}'
            data = json.dumps(message).encode()
            headers = {'Accept': 'application/json',
                       'Content-type': 'application/json',
                       'userid': self.user_id}

            req = request.Request(url=url, data=data, method='POST', headers=headers)

            response = request.urlopen(req).read()

            notification_response_str = json.loads(response)

            logger.info(f'알림톡 결과 : {notification_response_str}')

            is_notification_success = notification_response_str[0]['code']

            # 알림톡 발송 후 DB 에 발송된 내용 Insert
            if is_notification_success == 'success':
                is_success = 1
        except Exception as error:
            logger.critical(error, exc_info=True)
        finally:
            return is_success

    def get_notification_message(self, data, profile_key, receive_number, reservation_date):

        try:

            is_success = 0

            logger.debug(data)
            data['message_type'] = data['type']
            del data['type']

            data['tmplId'] = data['template_id']
            del data['template_id']

            data['msg'] = data['message']
            del data['message']

            if reservation_date == '':
                data['reserveDt'] = "00000000000000"
            else:
                data['reserveDt'] = reservation_date

            data['phn'] = receive_number
            data['profile'] = profile_key

            message = [data]
            return message

        except Exception as error:
            logger.critical(error, exc_info=True)
            message = ''

        finally:
            return message
