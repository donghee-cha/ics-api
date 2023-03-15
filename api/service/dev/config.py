import gc

from api import SessionLocal
from api.model.installer_member import InstallerMemberClass
from api.model.partner import PartnerClass
from api.model.kiosk_service import KioskServiceClass

from api.util.helper.decorator import parameter_validation
from api.util.helper.time import currentUTCTimestamp
from api.util.reponse_message import response_message_handler

import logging
import json

logger = logging.getLogger(__name__)


@parameter_validation(requires={'device_code': str, 'signage_flag': bool})
def get_config_info(data, header):
    response = dict()
    device_code = ''
    auth_token = ''

    db = SessionLocal()
    try:
        logger.info("header : {}".format(header))
        logger.info("data : {}".format(data))

        partner_info = db.query(PartnerClass).filter_by(partner_auth_token=header['Auth-Token'])

        if partner_info.count() > 0:

            # 디바이스 서비스 정보
            kiosk_service_info = db.query(KioskServiceClass).filter_by(device_code=data['device_code'],
                                                                       active=1,
                                                                       signage_flag=int(eval(data['signage_flag'])))

            if kiosk_service_info.count() > 0:
                kiosk_service_info_dict = kiosk_service_info.first().__dict__

                # 디바이스 파트너 정보
                kiosk_partner_info = db.query(PartnerClass).filter_by(
                    partner_code=kiosk_service_info_dict['ec_partner_code'])

                if kiosk_partner_info.count() > 0:

                    kiosk_partner_info = kiosk_partner_info.first().__dict__

                    service_config = kiosk_service_info_dict['service_config']
                    if service_config != '':
                        service_config_json = json.loads(service_config)
                        logger.debug(service_config_json)
                        if kiosk_service_info_dict['printer_flag'] == 0:
                            if 'receiptPrinterName' in service_config_json[0]['AppConfig']:
                                del service_config_json[0]['AppConfig']['receiptPrinterName']
                            if 'prescriptionPrinterName' in service_config_json[0]['AppConfig']:
                                del service_config_json[0]['AppConfig']['prescriptionPrinterName']
                            if 'defaultPrinterName' in service_config_json[0]['AppConfig']:
                                del service_config_json[0]['AppConfig']['defaultPrinterName']

                        service_config_json[0]['AppConfig']['authToken'] = kiosk_partner_info['partner_auth_token']
                        service_config_json[0]['AppConfig']['partnerKey'] = kiosk_service_info_dict[
                            'ec_partner_code']
                        service_config_json[0]['AppConfig']['device'] = data['device_code']
                        service_config_json[0]['AppConfig']['partnerName'] = kiosk_partner_info['partner_name']

                    else:
                        return response_message_handler(204, result_message='키오스크의 서비스 컨피그 정보가 존재하지 않습니다.')

                else:
                    logger.info("키오스크의 파트너사 정보가 존재하지 않습니다")
                    return response_message_handler(204)
            else:
                logger.info("키오스크 서비스 정보가 존재하지 않습니다")
                return response_message_handler(204)

            return response_message_handler(200, result_detail=service_config_json)
        else:
            return response_message_handler(401)

    except Exception as error:
        logger.critical(error, exc_info=True)
        return response_message_handler(500), 500

    finally:
        db.close()
        gc.collect()


@parameter_validation(requires={'device_code': str, 'installer_cellphone': str, 'service_config': str,
                                'signage_flag': bool})
def set_config_info(data, header):
    db = SessionLocal()

    try:
        logger.info("header : {}".format(header))
        logger.info("data : {}".format(data))

        partner_info = db.query(PartnerClass).filter_by(partner_auth_token=header['Auth-Token'])

        if partner_info.count() > 0:

            installer_member_info = db.query(InstallerMemberClass).filter_by(cellphone=data['installer_cellphone'],
                                                                             active=1)

            if installer_member_info.count() > 0:

                installer_member_info = installer_member_info.first().__dict__

                # 디바이스 서비스 정보
                kiosk_service_info = db.query(KioskServiceClass).filter_by(device_code=data['device_code'],
                                                                           active=1,
                                                                           signage_flag=int(eval(data['signage_flag'])))

                if kiosk_service_info.count() > 0:
                    kiosk_service_info_dict = kiosk_service_info.first().__dict__

                    # 디바이스 파트너 정보
                    kiosk_partner_info = db.query(PartnerClass).filter_by(
                        partner_code=kiosk_service_info_dict['ec_partner_code'])

                    if kiosk_partner_info.count() > 0:

                        if 'AppConfig' in data['service_config']:
                            service_config = data['service_config'].replace("\r\n", "")
                            logger.info(f' 컨피그 문자열 변경 : {service_config}')
                            kiosk_service_info.first().service_config = service_config
                            kiosk_service_info.first().installer_seq = installer_member_info['seq']
                            kiosk_service_info.first().status = 200
                            kiosk_service_info.first().update_date = currentUTCTimestamp()

                            try:
                                db.commit()

                            except Exception as error:
                                logger.critical(error, exc_info=True)
                                db.rollback()
                                return response_message_handler(500)

                            return response_message_handler(200)

                        else:
                            return response_message_handler(400, result_message='Config 에 AppConfig 정보가 누락되었습니다.')
                    else:
                        logger.info("키오스크의 파트너사 정보가 존재하지 않습니다")
                        return response_message_handler(204, result_message='키오스크의 파트너사 정보가 존재하지 않습니다.')

                else:
                    return response_message_handler(204)

            else:
                return response_message_handler(401)

        else:
            return response_message_handler(401)

    except Exception as error:
        logger.critical(error, exc_info=True)
        return response_message_handler(500), 500

    finally:
        db.close()
        gc.collect()
