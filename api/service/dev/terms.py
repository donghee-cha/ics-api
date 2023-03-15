import gc

from api import SessionLocal

from api.model.partner import PartnerClass
from api.model.terms import TermsClass
from api.util.reponse_message import response_message_handler

import logging

logger = logging.getLogger(__name__)

"""

ics 개인정보 이용동의 내역 가져오기

"""


def get_terms(data, header):
    db = SessionLocal()
    try:

        logger.info("header : {}".format(header))
        logger.info("data : {}".format(data))

        auth_token = header['Auth-Token']

        partner_info = db.query(PartnerClass).filter_by(partner_auth_token=auth_token)

        if partner_info.count() > 0:

            get_terms_list = db.query(TermsClass).filter_by(service_type='ics',
                                                            ec_partner_code=partner_info.first().partner_code). \
                order_by(TermsClass.is_need_agree.desc(), TermsClass.create_date.desc())

            terms_list = []
            if get_terms_list.count() > 0:
                for row in get_terms_list.all():
                    terms = dict()
                    terms['seq'] = row.seq
                    terms['is_need_agree'] = row.is_need_agree
                    terms['policy_name'] = row.name
                    terms['policy_information'] = row.information
                    terms_list.append(terms)

                return response_message_handler(200, result_detail=terms_list)

            else:
                return response_message_handler(204)

        else:
            return response_message_handler(401)

    except Exception as error:
        logger.critical(error, exc_info=True)
        return response_message_handler(500)

    finally:
        db.close()
        gc.collect()
