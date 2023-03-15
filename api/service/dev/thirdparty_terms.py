import gc

from api import SessionLocal

from api.model.partner import PartnerClass
from api.model.terms import TermsClass
from api.model.thirdparty_terms import ThirdPartyTermsClass
from api.util.helper.decorator import parameter_validation
from api.util.reponse_message import response_message_handler

import logging

logger = logging.getLogger(__name__)

"""

제3자 외부 서비스 이용약관 가져오기

"""


@parameter_validation(requires={'name': str})
def get_thirdparty_terms(data, header):
    db = SessionLocal()
    try:

        logger.info("header : {}".format(header))
        logger.info("data : {}".format(data))

        auth_token = header['Auth-Token']

        partner_info = db.query(PartnerClass).filter_by(partner_auth_token=auth_token)

        if partner_info.count() > 0:

            get_thirdparty_terms_list = db.query(ThirdPartyTermsClass).filter_by(thirdparty_name=data['name'])

            thirdparty_terms_list = []
            if get_thirdparty_terms_list.count() > 0:
                for row in get_thirdparty_terms_list.all():
                    terms = dict()
                    terms['seq'] = row.seq
                    terms['thirdparty_name'] = row.thirdparty_name
                    terms['thirdparty_type'] = row.thirdparty_type
                    terms['is_need_agree'] = row.is_need_agree
                    terms['name'] = row.name
                    terms['information'] = row.information
                    thirdparty_terms_list.append(terms)

                return response_message_handler(200, result_detail=thirdparty_terms_list)

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
