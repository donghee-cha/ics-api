from functools import wraps, update_wrapper
from flask import request, make_response

from datetime import datetime
from api.util.helper.auth_helper import check_header_auth_param
from api.util.helper.param_helper import check_required_param, check_required_form_data
from api.util.reponse_message import response_message_handler

import logging, json
logger = logging.getLogger(__name__)
"""
 필수 요청 헤더 ( auth-token ) 체크
"""


def token_required(f):
    # wraps를 이용해서 감싸져있는 함수를 디버깅 할 수 있다.
    @wraps(f)
    def decorated(*args, **kwargs):
        logger.info(f"<<<<<<<<<<[REQUEST API HOST ] {request.headers.get('Host')} >>>>>>>>>>>")
        data, status = check_header_auth_param(request)
        token = data.get('data')
        logger.info(f"<<<<<<<<<<[REQUEST API TOKEN ] {token} >>>>>>>>>>>")
        if not token:
            logger.info("<<<<<<<<<<[ERROR 발생!! ] 토큰이 존재하지 않습니다 >>>>>>>>>>>")
            return json.dumps(data, ensure_ascii=False), status

        return f(*args, **kwargs)

    return decorated


"""
 캐시 비활성화
"""


def nocache(view):
    @wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers['Last-Modified'] = datetime.now()
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response

    return update_wrapper(no_cache, view)


"""
 파라미터 유효성 체크
"""


def parameter_validation(**config):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            logger.info(f'<<<<<<<<<<[REQUEST API URL ] {request.path} >>>>>>>>>>> ')
            if request.method == 'POST':

                # POST 필수 값 검증
                is_validate = check_required_form_data(request, config['requires'])
                if is_validate == 1:
                    return f(*args, **kwargs)
                else:
                    return response_message_handler(400)
            elif request.method == 'GET':

                # GET 필수 값 검증
                is_validate = check_required_param(request, config['requires'])

                if is_validate == 1:
                    return f(*args, **kwargs)
                else:
                    return response_message_handler(400)

        return decorated_function

    return decorator
