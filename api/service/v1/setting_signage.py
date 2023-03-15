import gc

from api import SessionLocal
from api.model.installer_member import InstallerMemberClass
from api.model.kiosk_service_config import KioskServiceConfigClass
from api.model.partner import PartnerClass
from api.model.kiosk_service import KioskServiceClass

from api.util.helper.decorator import parameter_validation
from api.util.helper.time import currentUTCTimestamp
from api.util.reponse_message import response_message_handler

import logging
import json

logger = logging.getLogger(__name__)


@parameter_validation(requires={'device_code': str, 'installer_cellphone': str})
def set_install_signage_info(data, header):
    db = SessionLocal()

    try:
        logger.debug("header : {}".format(header))
        logger.debug("data : {}".format(data))

        partner_info = db.query(PartnerClass).filter_by(partner_auth_token=header['Auth-Token'])

        if partner_info.count() > 0:

            installer_member_info = db.query(InstallerMemberClass).filter_by(cellphone=data['installer_cellphone'],
                                                                             active=1)

            if installer_member_info.count() > 0:

                installer_member_info = installer_member_info.first().__dict__

                # 디바이스 서비스 정보
                kiosk_service_info = db.query(KioskServiceClass).filter_by(device_code=data['device_code'],
                                                                           signage_flag=1,
                                                                           active=1)

                if kiosk_service_info.count() > 0:
                    kiosk_service_info_dict = kiosk_service_info.first().__dict__

                    # 디바이스 파트너 정보
                    kiosk_partner_info = db.query(PartnerClass).filter_by(
                        partner_code=kiosk_service_info_dict['ec_partner_code'])

                    if kiosk_partner_info.count() > 0:

                        kiosk_partner_info = kiosk_partner_info.first().__dict__

                        service_seq = kiosk_service_info_dict['service_seq']
                        service_version = kiosk_service_info_dict['service_version']

                        service_version_info = db.query(KioskServiceConfigClass).filter_by(
                            service_version=service_version,
                            service_seq=service_seq)

                        if service_version_info.count() > 0:
                            service_version_info = service_version_info.first().__dict__
                            service_config = service_version_info['config']

                            service_config_json = json.loads(service_config)
                            service_config_json[0]['AppConfig']['authToken'] = kiosk_partner_info['partner_auth_token']
                            service_config_json[0]['AppConfig']['partnerName'] = kiosk_partner_info['partner_name']
                            service_config_json[0]['AppConfig']['device'] = data['device_code']
                            service_config_json[0]['AppConfig']['partnerKey'] = kiosk_service_info_dict[
                                'ec_partner_code']
                            if kiosk_service_info_dict['installed_date'] == 0:

                                kiosk_service_info.first().installed_date = currentUTCTimestamp()
                                kiosk_service_info.first().installer_seq = installer_member_info['seq']
                                kiosk_service_info.first().status = 200
                                kiosk_service_info.first().update_date = currentUTCTimestamp()
                            else:
                                kiosk_service_info.first().installed_date = currentUTCTimestamp()
                                kiosk_service_info.first().installer_seq = installer_member_info['seq']
                                kiosk_service_info.first().update_date = currentUTCTimestamp()
                            try:
                                db.commit()
                            except Exception as error:
                                logger.critical(error, exc_info=True)
                                db.rollback()
                                return response_message_handler(500)
                        else:
                            logger.info("서비스 컨피그 정보가 존재하지 않습니다")
                            return response_message_handler(204)

                    else:
                        logger.info("키오스크의 파트너사 정보가 존재하지 않습니다")
                        return response_message_handler(204)
                else:
                    logger.info("사이니지 서비스 정보가 존재하지 않습니다")
                    return response_message_handler(204)

                return response_message_handler(200, result_detail=service_config_json)
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
