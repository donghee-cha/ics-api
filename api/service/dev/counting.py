import gc
import json

from api import SessionLocal
from api.model.kiosk_service import KioskServiceClass

from api.model.statistic_print_count_data import StatisticPrintCountData
from api.model.partner import PartnerClass
from api.util.helper.decorator import parameter_validation
from api.util.helper.time import currentUTCTimestamp
from api.util.reponse_message import response_message_handler

import logging

logger = logging.getLogger(__name__)


@parameter_validation(requires={'device_code': str, 'history_id': str, 'service_type': int, 'count_time': int,
                                'count_list': str})
def set_counting_print_count(data, header):
    db = SessionLocal()

    try:

        logger.info("header : {}".format(header))
        logger.info("data : {}".format(data))

        auth_token = header['Auth-Token']

        partner_info = db.query(PartnerClass).filter_by(partner_auth_token=auth_token)

        if partner_info.count() > 0:

            partner_info = partner_info.first().__dict__
            get_kiosk_info = db.query(KioskServiceClass).filter_by(device_code=data['device_code'],
                                                                   ec_partner_code=partner_info['partner_code'])
            if get_kiosk_info.count() > 0:

                count_list = json.loads(data['count_list'])

                for count_info in count_list:

                    if 'document_code' in count_info and 'print_count' in count_info and 'file_count' in count_info \
                            and count_info['document_code'] != '' and count_info['print_count'] != '' \
                            and count_info['file_count'] != '':

                        if type(count_info['print_count']) == int:

                            new_print_count_data = StatisticPrintCountData(
                                partner_code=partner_info['partner_code'],
                                device_code=data['device_code'],
                                service_type=data['service_type'],
                                history_id=data['history_id'],
                                document_code=count_info['document_code'],
                                print_count=count_info['print_count'],
                                file_count=count_info['file_count'],
                                count_date=data['count_time'],
                                create_date=int(currentUTCTimestamp())
                               )
                            try:
                                db.add(new_print_count_data)
                                db.commit()

                            except Exception as error:
                                logger.critical(error, exc_info=True)
                                db.rollback()
                                return response_message_handler(500)
                        else:
                            return response_message_handler(400)

                    else:
                        return response_message_handler(400)

                return response_message_handler(200)

            else:
                return response_message_handler(403)

        else:
            return response_message_handler(401)

    except Exception as error:
        logger.critical(error, exc_info=True)
        return response_message_handler(500)
    finally:
        db.close()
        gc.collect()
