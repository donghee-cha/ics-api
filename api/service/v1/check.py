import gc

from api import SessionLocal

from api.model.kiosk_service import KioskServiceClass
from api.model.kiosk_service_status_log import KioskServiceStatusLog
from api.model.partner import PartnerClass
from api.util.helper.decorator import parameter_validation
from api.util.helper.time import currentUTCTimestamp
from api.util.reponse_message import response_message_handler

import logging

logger = logging.getLogger(__name__)


@parameter_validation(requires={'device_code': str, 'check_time': int})
def update_kiosk_program_status(data, header):
    db = SessionLocal()

    try:

        logger.debug("header : {}".format(header))
        logger.debug("data : {}".format(data))

        auth_token = header['Auth-Token']

        status_message = ''
        if 'message' in data:
            status_message = data['message']

        partner_info = db.query(PartnerClass).filter_by(partner_auth_token=auth_token)

        if partner_info.count() > 0:

            partner_info = partner_info.first().__dict__
            get_kiosk_info = db.query(KioskServiceClass).filter_by(device_code=data['device_code'],
                                                                   ec_partner_code=partner_info['partner_code'])
            if get_kiosk_info.count() > 0:

                new_kiosk_status_log = KioskServiceStatusLog(ec_partner_code=partner_info['partner_code'],
                                                             device_code=data['device_code'],
                                                             status_check_time=int(data['check_time']),
                                                             status_message=status_message,
                                                             create_date=int(currentUTCTimestamp())
                                                             )

                try:
                    db.add(new_kiosk_status_log)
                    db.commit()
                except Exception as error:
                    logger.critical(error, exc_info=True)
                    db.rollback()
                    return response_message_handler(500)
                finally:
                    db.close()

                return response_message_handler(200)

            else:
                return response_message_handler(204, result_message='해당 키오스크 기기가 파트너사에 일치하지 않습니다.')

        else:
            logger.debug('<<<<<<<<<<<[NOT FOUND] 파트너사 정보가 조회되지 않습니다>>>>>>>>>>')
            return response_message_handler(401)

    except Exception as error:
        logger.critical(error, exc_info=True)
        return response_message_handler(500)
    finally:
        db.close()
        gc.collect()
