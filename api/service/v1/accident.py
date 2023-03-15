import gc

from api import SessionLocal

from api.model.claim_history import ClaimClass
from api.util.helper.decorator import parameter_validation
from api.util.helper.time import *
from api.util.reponse_message import response_message_handler

import logging

logger = logging.getLogger(__name__)

"""

ics 청구할 사고정보 등록하기

"""


@parameter_validation(requires={'claim_id': str, 'claim_type': str,
                                'accident_type': int, 'accident_date': int,
                                'treat_code': str})
def save_accident_info(data, header):

    db = SessionLocal()

    try:

        logger.debug("header : {}".format(header))
        logger.debug("data : {}".format(data))

        diagnosis_name = ""
        if 'diagnosis_name' in data and data['diagnosis_name'] != '':
            diagnosis_name = data['diagnosis_name']

        get_claim_info = db.query(ClaimClass).filter_by(claim_id=data['claim_id'])

        if get_claim_info.count() > 0:

            partner_auth_token = get_claim_info.first().ec_partner_auth_token

            auth_token = header['Auth-Token']

            if auth_token == partner_auth_token:

                current_time_stamp = currentUTCTimestamp()
                get_claim_info.first().claim_type = data['claim_type']
                get_claim_info.first().accident_type = data['accident_type']
                get_claim_info.first().accident_date = data['accident_date']
                get_claim_info.first().treat_code = data['treat_code']
                get_claim_info.first().diagnosis_name = diagnosis_name
                get_claim_info.first().update_date = current_time_stamp

                try:
                    db.commit()

                except Exception as error:
                    logger.critical(error, exc_info=True)
                    db.rollback()
                    return response_message_handler(500)

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


"""

ics 청구할 사고정보 가져오기

"""


@parameter_validation(requires={'claim_id': str})
def get_accident_list(data, header):

    db = SessionLocal()

    try:

        logger.debug("header : {}".format(header))
        logger.debug("data : {}".format(data))

        # 사용자 정보를 가져와서 고객사 코드와 비교하기
        get_claim_info = db.query(ClaimClass).filter_by(claim_id=data['claim_id'])

        if get_claim_info.count() > 0:
            get_claim_info_dict = get_claim_info.first().__dict__
            partner_auth_token = get_claim_info_dict['ec_partner_auth_token']

            auth_token = header['Auth-Token']

            if auth_token == partner_auth_token:

                accident_info = dict()

                # 데이터가 없는지 확인
                if get_claim_info_dict['claim_type'] == '0' and get_claim_info_dict['accident_type'] == 0 \
                        and get_claim_info_dict['accident_date'] == 0 and get_claim_info_dict['treat_code'] == "" \
                        and get_claim_info_dict['diagnosis_name'] == "":
                    return response_message_handler(204)

                else:

                    accident_info['claim_type'] = get_claim_info_dict['claim_type']
                    accident_info['accident_type'] = get_claim_info_dict['accident_type']

                    # 사고 년,월,일
                    if get_claim_info.first().accident_date > 0:
                        accident_time_stamp = get_claim_info_dict['accident_date'] + (9 * 3600)
                        accident_data = convertTimeToYYYYMMDDList(accident_time_stamp)
                        accident_info['accident_year'] = accident_data['year']
                        accident_info['accident_month'] = accident_data['month']
                        accident_info['accident_day'] = accident_data['day']

                    else:
                        accident_info['accident_year'] = ''
                        accident_info['accident_month'] = ''
                        accident_info['accident_day'] = ''

                    accident_info['treat_code'] = get_claim_info_dict['treat_code']
                    accident_info['diagnosis_name'] = get_claim_info_dict['diagnosis_name']

                    return response_message_handler(200, result_detail=accident_info)

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
