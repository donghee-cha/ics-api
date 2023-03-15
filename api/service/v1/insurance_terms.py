import gc
import json

from api import SessionLocal

from api.model.insurance import InsuranceClass
from api.util.reponse_message import response_message_handler
from api.util.plugin.cipher import AESCipher

import logging

logger = logging.getLogger(__name__)

"""

선택한 보험사의 약관동의 정보 가져오기

"""


def get_insurance_terms_list(data, header):
    db = SessionLocal()
    try:

        cipher = AESCipher()

        print(cipher.decrypt('publicndscoreapi', 'HCrjePTrFbQGbalucXpYMg=='))
        set_insurance_terms_list = []

        logger.debug("header : {}".format(header))
        logger.debug("data : {}".format(data))

        if 'insurance_code_list' in data and data['insurance_code_list'] != '':
            insurance_code_list = []
            if ',' in data['insurance_code_list']:
                insurance_code_list = data['insurance_code_list'].split(',')
            else:
                insurance_code_list.append(data['insurance_code_list'])

            for insurance_code in insurance_code_list:

                get_insurance_info = db.query(InsuranceClass).filter_by(active=1, ec_code=insurance_code)
                if get_insurance_info.count() > 0:
                    get_insurance_info = get_insurance_info.first().__dict__

                    if get_insurance_info['terms_information'] != '':

                        terms_information = json.loads(get_insurance_info['terms_information'])
                        set_insurance_terms_info = dict(insurance_code=get_insurance_info['ec_code'],
                                                        is_need_agree=terms_information['is_need_agree'],
                                                        policy_name=terms_information['policy_name'],
                                                        policy_information=terms_information['policy_information'])
                    else:
                        set_insurance_terms_info = dict(insurance_code='',
                                                        is_need_agree=False,
                                                        policy_name='',
                                                        policy_information='')

                    set_insurance_terms_list.append(set_insurance_terms_info)

                else:
                    return response_message_handler(400)

            return response_message_handler(200, result_detail=set_insurance_terms_list)
        else:
            get_insurance_list = db.query(InsuranceClass).filter_by(active=1).all()

            for get_insurance in get_insurance_list:
                get_insurance = get_insurance.__dict__
                logger.debug(get_insurance)
                if get_insurance['terms_information'] != '':
                    terms_information = json.loads(get_insurance['terms_information'])
                    set_insurance_terms_info = dict(insurance_code=get_insurance['ec_code'],
                                                    is_need_agree=terms_information['is_need_agree'],
                                                    policy_name=terms_information['policy_name'],
                                                    policy_information=terms_information['policy_information'])
                else:
                    set_insurance_terms_info = dict(insurance_code=get_insurance['ec_code'],
                                                    is_need_agree=False,
                                                    policy_name='',
                                                    policy_information='')


                set_insurance_terms_list.append(set_insurance_terms_info)

            return response_message_handler(200, result_detail=set_insurance_terms_list)

    except Exception as error:
        logger.critical(error, exc_info=True)
        return response_message_handler(500)

    finally:
        db.close()
        gc.collect()
