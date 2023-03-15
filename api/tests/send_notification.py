import json
from urllib import request, parse
import urllib

"""
비즈엠 알림톡
"""


class SendNotification:

    def __init__(self):
        self.api_url = "https://alimtalk-api.bizmsg.kr"
        self.user_id = "ahnmi422"
        self.profile = "18cf06274ff4396c775161bb749ae6038eda0a73"

    # 알림톡 전송
    def send_notification(self, receive_phone, message):
        url = f'{self.api_url}/v2/sender/send'
        tmpl_id = "evcare_010"
        document_url = "http://www.evcare.kr"
        fax_url = "http://www.evcare.kr"

        button_one = {
            "name": "서류 첨부하기",
            "type": "WL",
            "url_mobile": document_url,
            "url_pc": document_url
        }
        button_two = {
            "name": "개인 팩스번호 등록",
            "type": "WL",
            "url_mobile": fax_url,
            "url_pc": fax_url
        }

        data = [{"message_type": "at",
                 "profile": self.profile,
                 "phn": receive_phone,
                 "tmplId": tmpl_id,
                 "msg": message,
                 "reserveDt": "00000000000000",
                 "button1": button_one,
                 "button2": button_two
                 }]
        #
        data = json.dumps(data).encode()
        print('data : {}'.format(data))
        # # data = parse.urlencode(data).encode('utf-8')
        headers = {'Accept': 'application/json',
                   'Content-type': 'application/json',
                   'userid': self.user_id}

        req = request.Request(url=url, data=data, headers=headers)

        response = urllib.request.urlopen(req)
        jsonResponse = json.loads(response.read())
        print('jsonResponce : {}'.format(jsonResponse))



"""
알림톡 테스트 시작
"""

# message = "테스터 님의  보험금 청구 신청서가 접수완료 되었습니다.\n서류 첨부까지 진행하셔야 보험금 청구 신청이 완료됩니다.\n\n▶ 서류 첨부하기 : 미등록시 신청서 접수가 취소 처리 됩니다.\n▶ 개인팩스 번호 등록 : 총 2건이 등록되어야 합니다.\n▶ 보험사 : 삼성화재,동부화재\n▶ 이용 병원명 : 이브이케어\n▶ 청구 신청서 접수 일자 : 2021.07.13"
#
# send_notification = SendNotification()
# receive_phone = '821024105126'
#
# send_notification.send_notification(receive_phone, message)

"""
알림톡 테스트 끝
"""
