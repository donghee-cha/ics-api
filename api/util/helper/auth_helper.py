"""
인증 헬퍼 입니다
"""


def check_header_auth_param(new_request):
    auth_token = new_request.headers.get('Auth-Token')

    if auth_token:
        response_object = {
            'result_code': '200',
            'data': auth_token
        }
        return response_object, 200
    else:

        response_object = {
            'result_code': '401',
            'result_message': '접근하기 위한 권한이 없습니다'
        }
        return response_object, 401
