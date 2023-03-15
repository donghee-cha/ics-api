import gc

from api import SessionLocal

from api.model.claim_history_dev import ClaimClass
from api.model.partner import PartnerClass

from api.util.helper.decorator import parameter_validation
from api.util.reponse_message import response_message_handler
from api.util.plugin.cipher import AESCipher

from api.config import secret_key

import logging

logger = logging.getLogger(__name__)

"""

ics auth-token 가져오기

"""


@parameter_validation(requires={'claim_id': str})
def get_auth_token_info(data, header):
    db = SessionLocal()

    try:

        cipher = AESCipher()

        logger.info("header : {}".format(header))
        logger.info("data : {}".format(data))

        auth_token = header['Auth-Token']

        partner_info = db.query(PartnerClass).filter_by(partner_auth_token=auth_token)

        if partner_info.count() > 0:

            partner_info = partner_info.first().__dict__

            # 이브이케어일 경우에만 해당 api를 쓸 수 있음.
            if partner_info['partner_code'] == 'evc2101':
                claim_info = db.query(ClaimClass).filter_by(claim_id=data['claim_id'])
                if claim_info.count() > 0:
                    claim_info = claim_info.first().__dict__

                    partner_info = db.query(PartnerClass).filter_by(partner_auth_token=
                                                                    claim_info['ec_partner_auth_token'])

                    if partner_info.count() > 0:

                        partner_info = partner_info.first().__dict__
                        enc_secret_key = cipher.encrypt(secret_key, partner_info['partner_secret_key'])
                        return response_message_handler(200, result_detail={
                            'auth-token': claim_info['ec_partner_auth_token'],
                            'secret-key': enc_secret_key})
                    else:
                        return response_message_handler(204)
                else:
                    return response_message_handler(204)
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
