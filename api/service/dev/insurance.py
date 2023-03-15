import gc

from api import SessionLocal

from api.model.claim_history_dev import ClaimClass
from api.util.helper.decorator import parameter_validation
from api.util.helper.time import currentUTCTimestamp
from api.util.reponse_message import response_message_handler

import logging

logger = logging.getLogger(__name__)

"""

ics 청구할 보험사 목록 등록하기

"""


@parameter_validation(requires={'claim_id': str, 'insurance_code_list': str})
def save_insurance_list(data, header):
    db = SessionLocal()
    try:

        logger.info("header : {}".format(header))
        logger.info("data : {}".format(data))

        get_claim_info = db.query(ClaimClass).filter_by(claim_id=data['claim_id'])

        if get_claim_info.count() > 0:

            partner_auth_token = get_claim_info.first().ec_partner_auth_token

            auth_token = header['Auth-Token']

            if auth_token == partner_auth_token:
                current_time_stamp = currentUTCTimestamp()

                get_claim_info.first().ec_insurance_code_list = data['insurance_code_list']
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

ics 청구할 보험사 목록 가져오기

"""


@parameter_validation(requires={'claim_id': str})
def get_insurance_list(data, header):
    db = SessionLocal()
    try:

        logger.info("header : {}".format(header))
        logger.info("data : {}".format(data))

        get_claim_info = db.query(ClaimClass).filter_by(claim_id=data['claim_id'])

        if get_claim_info.count() > 0:

            get_claim_info_dict = get_claim_info.first().__dict__

            partner_auth_token = get_claim_info_dict['ec_partner_auth_token']

            auth_token = header['Auth-Token']

            if auth_token == partner_auth_token:

                insurance_info = dict()

                if get_claim_info.count() > 0:

                    if get_claim_info_dict['ec_insurance_code_list'] == "":
                        return response_message_handler(204)

                    else:
                        insurance_info['insurance_code_list'] = get_claim_info_dict['ec_insurance_code_list']
                        return response_message_handler(200, result_detail=insurance_info)

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
