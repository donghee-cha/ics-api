import gc
import json
import logging
import types
from typing import Generic, TypeVar

import requests

logger = logging.getLogger(__name__)
T = TypeVar('T')


class InterfaceCallbackClass:

    # EMR URL 명시
    def __init__(self):
        pass

    def post(self, url, headers, callback_function, request_data):

        logger.debug(f'<<<<<<<< request post callback >>>>>>>>>> ')

        logger.info(f'[API 요청 DATA] : {request_data}')

        # request_data = json.dumps(request_data).encode('utf-8')
        response_data = dict(result_code=200, result_message='성공', result_detail=Generic[T])

        try:

            r = requests.post(url, data=request_data, headers=headers)
            r.encoding = 'UTF-8'
            data = r.text
            logger.info(f'[API 응답 DATA] : {data}')

            if type(callback_function) is types.FunctionType:

                response_data = callback_function(data)
            else:
                response_data = json.loads(data)

            del r

        except requests.Timeout as error:
            logger.critical(error, exc_info=True)
            response_data['result_code'] = 500
        except requests.ConnectionError as error:
            logger.critical(error, exc_info=True)
            response_data['result_code'] = 500
        except requests.HTTPError as error:
            logger.critical(error, exc_info=True)
            response_data['result_code'] = 500
        except requests.RequestException as error:
            logger.critical(error, exc_info=True)
            response_data['result_code'] = 500
        except Exception as error:
            logger.critical(error, exc_info=True)
            response_data['result_code'] = 500
        finally:
            gc.collect()
            return response_data

    def get(self, url, headers, callback_function, request_data):

        logger.debug(f'<<<<<<<< request get callback >>>>>>>>>> ')

        logger.info(f'[API 요청 DATA] : {request_data}')
        request_data = json.dumps(request_data).encode('utf-8')
        response_data = dict(result_code=4200, result_message='성공', result_detail=Generic[T])

        try:
            r = requests.get(url, data=str(request_data), headers=headers)
            r.encoding = 'UTF-8'
            data = r.text
            logger.info(f'[API 응답 DATA] : {r.text}')

            del r
            if type(callback_function) is types.FunctionType:

                response_data = callback_function(data)
            else:
                response_data = json.loads(data)

        except requests.Timeout as error:
            logger.critical(error, exc_info=True)
            response_data['result_code'] = 500
        except requests.ConnectionError as error:
            logger.critical(error, exc_info=True)
            response_data['result_code'] = 500
        except requests.HTTPError as error:
            logger.critical(error, exc_info=True)
            response_data['result_code'] = 500
        except requests.RequestException as error:
            logger.critical(error, exc_info=True)
            response_data['result_code'] = 500
        except Exception as error:
            logger.critical(error, exc_info=True)
            response_data['result_code'] = 500
        finally:
            gc.collect()
            return response_data

    def file_upload(self, url, callback_function, request_file, request_data):

        logger.debug(f'<<<<<<<< request post callback >>>>>>>>>> ')

        logger.info(f'[API 요청 DATA] : {request_data}')
        response_data = dict(result_code=200, result_message='성공', result_detail=Generic[T])

        try:
            r = requests.post(url, headers={'Content-Type': self.content_type},
                              files=request_file, data=request_data)
            r.encoding = 'UTF-8'
            data = r.text
            logger.info(f'[API 응답 DATA] : {r.text}')

            del r
            if type(callback_function) is types.FunctionType:

                response_data = callback_function(data)
            else:
                response_data = json.loads(data)

        except requests.Timeout as error:
            logger.critical(error, exc_info=True)
            response_data['result_code'] = 500
        except requests.ConnectionError as error:
            logger.critical(error, exc_info=True)
            response_data['result_code'] = 500
        except requests.HTTPError as error:
            logger.critical(error, exc_info=True)
            response_data['result_code'] = 500
        except requests.RequestException as error:
            logger.critical(error, exc_info=True)
            response_data['result_code'] = 500
        except Exception as error:
            logger.critical(error, exc_info=True)
            response_data['result_code'] = 500
        finally:
            gc.collect()
            return response_data
