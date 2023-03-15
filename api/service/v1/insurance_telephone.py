import gc

from api import SessionLocal

from api.model.claim_history import ClaimClass
from api.model.insurance import InsuranceClass
from api.util.helper.decorator import parameter_validation
from api.util.reponse_message import response_message_handler

import logging

logger = logging.getLogger(__name__)

"""

ics 개인팩스번호 등록할 보험사의 콜센터 정보 가져오기

"""


@parameter_validation(requires={'claim_id': str})
def get_insurance_telephone_info(data, header):
    db = SessionLocal()
    try:

        logger.debug("header : {}".format(header))
        logger.debug("data : {}".format(data))

        get_claim_info = db.query(ClaimClass).filter_by(claim_id=data['claim_id'])

        if get_claim_info.count() > 0:

            get_claim_info_dict = get_claim_info.first().__dict__

            partner_auth_token = get_claim_info_dict['ec_partner_auth_token']

            auth_token = header['Auth-Token']

            if auth_token == partner_auth_token:

                insurance_code_list = get_claim_info_dict['ec_insurance_code_list']

                if insurance_code_list == "":
                    return response_message_handler(204)
                else:

                    insurance_code_arr = insurance_code_list.split(',')

                    insurance_telephone_list = []
                    get_insurance_info = dict()

                    for insurance in insurance_code_arr:

                        get_insurance = dict()
                        insurance = insurance.strip()

                        insurance_info = db.query(InsuranceClass).filter_by(active=1, ec_code=insurance)

                        if insurance_info.count() > 0:

                            # 개인 팩스번호가 필요한 보험사인지 확인
                            if insurance_info.first().claim_type == 2:

                                get_insurance['insurance_code'] = insurance_info.first().ec_code
                                get_insurance['telephone'] = insurance_info.first().service_telephone

                                insurance_telephone_list.append(get_insurance)

                    get_insurance_info['insurance_telephone'] = insurance_telephone_list

                    return response_message_handler(200, result_detail=get_insurance_info)

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
