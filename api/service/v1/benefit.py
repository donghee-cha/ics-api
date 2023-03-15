import gc
import json
import logging

from api import SessionLocal
from api.config import default_hospital_seq, default_hospital_code
from api.model.district_sido import DistrictSidoClass
from api.model.benefit import BenefitClass
from api.model.benefit_application import BenefitApplicationClass
from api.model.district_sigungu import DistrictSigunguClass
from api.model.hospital import HospitalClass
from api.model.partner import PartnerClass
from api.util.helper.decorator import parameter_validation
from api.util.helper.time import currentUTCTimestamp
from api.util.plugin.cipher import AESCipher
from api.util.reponse_message import response_message_handler

logger = logging.getLogger(__name__)


@parameter_validation(requires={'benefit_code': str})
def get_benefit_info(header, data):
    try:
        result_list = []

        db = SessionLocal()

        logger.debug("header : {}".format(header))
        logger.debug("data : {}".format(data))

        """ -----------benefit_code 고정값 시작----------- """
        data['benefit_code'] = 'EVT2200001'
        """ -----------benefit_code 고정값 끝 -----------"""

        event_info = db.query(BenefitClass).filter_by(code=data['benefit_code'])

        if event_info.count() > 0:
            event_info = event_info.first().__dict__
            result_dict = dict()
            result_dict['name'] = event_info['name']
            result_dict['start_date'] = event_info['start_date']
            result_dict['end_date'] = event_info['end_date']

            if event_info['terms_information'] != '':
                terms_info = event_info['terms_information']
                terms_info_json = json.loads(terms_info)
                result_dict['terms_list'] = terms_info_json

            result_list.append(result_dict)

            return response_message_handler(200, result_detail=result_dict)

        else:
            response_message_handler(204)

    except Exception as error:
        logger.error(error, exc_info=True)
        return response_message_handler(500)

    finally:
        gc.collect()


@parameter_validation(requires={'benefit_code': str, 'device': str, 'name': str, 'cellphone': str})
def set_benefit_participate(header, data):
    try:

        logger.debug("header : {}".format(header))
        logger.debug("data : {}".format(data))

        hospital_name = ''
        hospital_code = ''
        applicant_name = data['name'].strip()
        applicant_cellphone = data['cellphone'].strip()
        sido_code = 31
        sigungu_code = 310403

        cipher = AESCipher()
        db = SessionLocal()
        current_time_stamp = currentUTCTimestamp()

        partner_info = db.query(PartnerClass).filter_by(partner_auth_token=header['Auth-Token'])

        if partner_info.count() > 0:

            partner_info = partner_info.first().__dict__

            # 복호화
            partner_secret_key = partner_info['partner_secret_key']
            applicant_name = cipher.decrypt(partner_secret_key, applicant_name)
            applicant_cellphone = cipher.decrypt(partner_secret_key, applicant_cellphone)

            benefit_info = db.query(BenefitClass).filter_by(code=data['benefit_code'])

            if benefit_info.count() > 0:
                benefit_info = benefit_info.first().__dict__

                benefit_partner_info = db.query(PartnerClass).filter_by(partner_code=benefit_info['partner_code'])
                if benefit_partner_info.count() > 0:
                    benefit_partner_info = benefit_partner_info.first().__dict__

                    # 혜택 고객사에 맞게 암호화
                    benefit_partner_secret_key = benefit_partner_info['partner_secret_key']
                    applicant_name = cipher.encrypt(benefit_partner_secret_key, applicant_name)
                    applicant_cellphone = cipher.encrypt(benefit_partner_secret_key, applicant_cellphone)

                    benefit_application_info = db.query(BenefitApplicationClass).filter_by(
                        applicant_name=applicant_name,
                        applicant_cellphone=applicant_cellphone,
                        benefit_code=data['benefit_code'])
                    if benefit_application_info.count() == 0:
                        
                        # 병원 정보 가져오기
                        if partner_info['hospital_seq'] > 0:

                            hospital_info = db.query(HospitalClass).filter_by(
                                seq=partner_info['hospital_seq'], active=1)

                            if hospital_info.count() == 0:
                                hospital_info = db.query(HospitalClass).filter_by(
                                    seq=default_hospital_seq, active=1)

                            hospital_info = hospital_info.first().__dict__
                            hospital_name = hospital_info['name']
                            hospital_code = hospital_info['code']
                            
                            # 병원코드가 기본코드가 아닐경우에만 시도, 시군구 코드를 가져옴
                            if hospital_code != default_hospital_code:
                                sido_code = int(hospital_code[0:2])
                                sigungu_code = int(hospital_code[0:6])

                            logger.debug(sido_code)
                            logger.debug(sigungu_code)

                            sido_info = db.query(DistrictSidoClass).filter_by(code=sido_code, active=1)
                            sigungu_info = db.query(DistrictSigunguClass).filter_by(code=sigungu_code, active=1)

                            if sido_info.count() > 0:
                                sido_info = sido_info.first().__dict__
                            if sigungu_info.count() > 0:
                                sigungu_info = sigungu_info.first().__dict__

                            # 신청자 id 발행 (현재 날짜 + timestamp + 현재 날짜에 따른 순서)
                            applicant_id = 'EVCARE'

                            # 추천인 정보
                            recommender = ''
                            if 'recommender' in data:
                                recommender = data['recommender']

                            new_benefit_history = BenefitApplicationClass(benefit_code=data['benefit_code'],
                                                                          device_code=data['device'],
                                                                          device_use_date=current_time_stamp,
                                                                          applicant_id=applicant_id,
                                                                          applicant_name=applicant_name,
                                                                          applicant_cellphone=applicant_cellphone,
                                                                          hospital_name=hospital_name,
                                                                          hospital_code=hospital_code,
                                                                          district_sido_code=sido_info['code'],
                                                                          district_sido_name=sido_info['name'],
                                                                          district_sigungu_code=sigungu_info['code'],
                                                                          district_sigungu_name=sigungu_info['name'],
                                                                          partner_code=partner_info['partner_code'],
                                                                          partner_recommender=recommender,
                                                                          create_date=current_time_stamp
                                                                          )
                            try:
                                db.add(new_benefit_history)
                                db.commit()
                            except Exception as error:
                                logger.critical(error, exc_info=True)
                                db.rollback()
                                return response_message_handler(500)

                            return response_message_handler(200)

                        else:
                            return response_message_handler(401)
                    else:
                        return response_message_handler(409)
                else:
                    return response_message_handler(204)
            else:
                return response_message_handler(204)
        else:
            return response_message_handler(401)

    except Exception as error:
        logger.error(error, exc_info=True)
        return response_message_handler(500)

    finally:
        gc.collect()
