import json
import logging

logger = logging.getLogger(__name__)

message = {
    200: "성공",
    204: "데이터가 존재하지 않습니다",
    400: "필수 파라미터가 전달되지 않은 경우 또는 유효하지 않은 파라미터인 경우입니다",
    401: "요청된 자원에 액세스하기 위한 권한이 없습니다",
    403: "허용되지 않는 서비스를 요청하였습니다",
    404: "요청한 페이지를 찾을 수 없습니다",
    405: "이 메소드 유형은 현재 지원되지 않습니다",
    408: "서버 네트워크가 끊겼습니다",
    409: "이미 있는 데이터 입니다",
    410: "현재 버전에서 지원하지 않는 기능입니다. 버전을 업데이트 해주세요",
    500: "예기치 않은 내부 서버 오류가 발생했습니다",
    503: "서버를 현재 이용할 수 없습니다",
}


# result_code, result_message 는 필수 이며 변경가능하다.
def response_message_handler(status_code, **kwargs):
    result = {
        'result_code': status_code,
        'result_message': message[status_code]
    }

    if kwargs.items().__len__() > 0:
        for key, value in kwargs.items():
            result[key] = value
    if result['result_code'] != 200:
        logger.info(f'<<<<<<<<<<[RESPONSE API STATUS CODE ] {result} >>>>>>>>>>> ')
        logger.info(f'<<<<<<<<<<[RESPONSE API MESSAGE ] {result} >>>>>>>>>>> ')

    return json.dumps(result, ensure_ascii=False)
