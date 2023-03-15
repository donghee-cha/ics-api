import gc

from api.config import default_partner_code
from api import SessionLocal
from api.model.hospital import HospitalClass
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


@parameter_validation(requires={'device_code': str, 'program_version': str, 'is_signage': int})
def get_available_install_info(data, header):
    db = SessionLocal()

    response = dict()
    available_flag = False
    available_false_information = ''
    hospital_name = ''
    partner_code = ''

    try:
        logger.debug("header : {}".format(header))
        logger.debug("data : {}".format(data))

        partner_info = db.query(PartnerClass).filter_by(partner_auth_token=header['Auth-Token'])

        if partner_info.count() > 0:
            partner_info = partner_info.first().__dict__

            # 정보 요청이 사이니지 타입일 경우 디바이스가 사이니지 정보가 있는지 확인한다.
            if int(data['is_signage']) == 1:

                kiosk_service_info = db.query(KioskServiceClass).filter_by(device_code=data['device_code'],
                                                                           active=1,
                                                                           signage_flag=1)
                if kiosk_service_info.count() > 0:
                    kiosk_service_info = kiosk_service_info.first().__dict__

                    if data['program_version'] == kiosk_service_info['service_version']:

                        # 병원 정보 불러오기
                        kiosk_partner_info = db.query(PartnerClass).filter_by(
                            partner_code=kiosk_service_info['ec_partner_code'])
                        if kiosk_partner_info.count() > 0:

                            kiosk_partner_info = kiosk_partner_info.first().__dict__
                            partner_code = kiosk_partner_info['partner_code']
                            hospital_info = db.query(HospitalClass).filter_by(
                                seq=kiosk_partner_info['hospital_seq'], active=1)

                            if hospital_info.count() > 0:
                                hospital_info = hospital_info.first().__dict__
                                hospital_name = hospital_info['name']

                        # 파트너사 코드가 신규로 들어온 경우
                        if partner_info['partner_code'] == default_partner_code:

                            if kiosk_service_info['installed_date'] > 0:
                                """
                               2022.07.12 임시수정 :: 기존 프로그램 업데이트 START  
                               """

                                # available_flag = False
                                available_flag = True

                                """
                                2022.07.12 임시수정 :: 기존 프로그램 업데이트 END
                                """

                            else:
                                if kiosk_service_info['active'] == 0:
                                    available_false_information = '현재 비활성화된 상태입니다'
                                elif int(kiosk_service_info['status']) > 900:
                                    available_false_information = '현재 철수 상태입니다.'
                                else:
                                    available_flag = True
                        else:
                            # 기기가 기존에 설치되었고 업데이트 상태일경우
                            if kiosk_service_info['installed_date'] > 0:
                                available_flag = True
                                available_false_information = '업데이트 상태입니다'
                            else:

                                if int(kiosk_service_info['status']) == 900:
                                    available_false_information = '회수 상태입니다'
                                elif 900 < int(kiosk_service_info['status']) < 999:
                                    available_false_information = '비활성화 상태입니다'
                                elif int(kiosk_service_info['status']) == 999:
                                    available_false_information = '철수 상태입니다'
                                else:
                                    if kiosk_service_info['active'] == 0:
                                        available_false_information = '비활성화된 상태입니다'
                                    else:
                                        available_flag = True

                    else:
                        available_false_information = "해당 디바이스의 서비스 프로그램 버전이 맞지 않습니다."
                else:
                    available_false_information = "해당 디바이스의 서비스 정보가 없습니다."

                response['hospital_name'] = hospital_name
                response['available_flag'] = available_flag
                response['available_false_information'] = available_false_information
                response['partner_code'] = partner_code

                return response_message_handler(200, result_detail=response)
            else:
                kiosk_service_info = db.query(KioskServiceClass).filter_by(device_code=data['device_code'],
                                                                           signage_flag=0,
                                                                           active=1)
                if kiosk_service_info.count() > 0:
                    kiosk_service_info = kiosk_service_info.first().__dict__

                    if data['program_version'] == kiosk_service_info['service_version']:

                        # 병원 정보 불러오기
                        kiosk_partner_info = db.query(PartnerClass).filter_by(
                            partner_code=kiosk_service_info['ec_partner_code'])
                        if kiosk_partner_info.count() > 0:

                            kiosk_partner_info = kiosk_partner_info.first().__dict__
                            partner_code = kiosk_partner_info['partner_code']
                            hospital_info = db.query(HospitalClass).filter_by(
                                seq=kiosk_partner_info['hospital_seq'], active=1)

                            if hospital_info.count() > 0:
                                hospital_info = hospital_info.first().__dict__
                                hospital_name = hospital_info['name']

                        # 파트너사 코드가 신규로 들어온 경우
                        if partner_info['partner_code'] == default_partner_code:

                            if kiosk_service_info['installed_date'] > 0:
                                """
                                2022.07.12 임시수정 :: 기존 프로그램 업데이트 START  
                                """

                                # available_flag = False
                                available_flag = True

                                """
                                2022.07.12 임시수정 :: 기존 프로그램 업데이트 END
                                """
                                available_false_information = '이미 설치된 기기 입니다'

                            else:
                                if kiosk_service_info['active'] == 0:
                                    available_false_information = '현재 비활성화된 상태입니다'
                                elif int(kiosk_service_info['status']) > 900:
                                    available_false_information = '현재 철수 상태입니다.'
                                else:
                                    available_flag = True
                        else:
                            # 기기가 기존에 설치되었고 업데이트 상태일경우
                            if kiosk_service_info['installed_date'] > 0:
                                available_flag = True
                                available_false_information = '업데이트 상태입니다'
                            else:

                                if int(kiosk_service_info['status']) == 900:
                                    available_false_information = '회수 상태입니다'
                                elif 900 < int(kiosk_service_info['status']) < 999:
                                    available_false_information = '비활성화 상태입니다'
                                elif int(kiosk_service_info['status']) == 999:
                                    available_false_information = '철수 상태입니다'
                                else:
                                    if kiosk_service_info['active'] == 0:
                                        available_false_information = '비활성화된 상태입니다'
                                    else:
                                        available_flag = True
                    else:
                        available_false_information = "해당 디바이스의 서비스 버전이 맞지 않습니다"

                else:
                    available_false_information = "해당 디바이스의 서비스 정보가 없습니다."

                response['hospital_name'] = hospital_name
                response['available_flag'] = available_flag
                response['available_false_information'] = available_false_information
                response['partner_code'] = partner_code

                return response_message_handler(200, result_detail=response)

        else:
            return response_message_handler(401)

    except Exception as error:
        logger.critical(error, exc_info=True)
        return response_message_handler(500), 500

    finally:
        db.close()
        gc.collect()


@parameter_validation(requires={'device_code': str, 'installer_cellphone': str})
def set_install_kiosk_info(data, header):
    response = dict()
    device_code = ''
    auth_token = ''

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
                                                                           signage_flag=0,
                                                                           active=1)

                if kiosk_service_info.count() > 0:
                    kiosk_service_info_dict = kiosk_service_info.first().__dict__

                    # 디바이스 파트너 정보
                    kiosk_partner_info = db.query(PartnerClass).filter_by(
                        partner_code=kiosk_service_info_dict['ec_partner_code'])

                    if kiosk_partner_info.count() > 0:

                        kiosk_partner_info = kiosk_partner_info.first().__dict__

                        service_version = kiosk_service_info_dict['service_version']
                        service_seq = kiosk_service_info_dict['service_seq']

                        service_version_info = db.query(KioskServiceConfigClass).filter_by(
                            service_seq=service_seq,
                            service_version=service_version)

                        # 디바이스 컨피그 정보
                        if service_version_info.count() > 0:
                            service_version_info = service_version_info.first().__dict__
                            service_config = service_version_info['config']

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
                    logger.info("키오스크 서비스 정보가 존재하지 않습니다")
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
