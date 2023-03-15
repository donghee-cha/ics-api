import gc

from api import SessionLocal
from api.config import default_hospital_seq
from api.model.bank import BankClass

from api.model.insurance import InsuranceClass
from api.model.partner import PartnerClass
from api.model.treat import TreatClass
from api.model.work import WorkClass
from api.util.reponse_message import response_message_handler

import logging

logger = logging.getLogger(__name__)

"""

전체 보험사 목록 조회하기

"""


def get_insurance_company_list(data, header):
    db = SessionLocal()

    insurance_code = data['insurance_code'] if 'insurance_code' in data and data['insurance_code'] != '' else ''
    set_insurance_list = []

    try:

        if insurance_code != '':

            insurance_list = db.query(InsuranceClass).filter_by(active=1, ec_code=insurance_code).all()

        else:
            insurance_list = db.query(InsuranceClass).filter_by(active=1).order_by(InsuranceClass.ec_code).all()

        if len(insurance_list) > 0:
            for insurance_item in insurance_list:
                set_essential_item_list = []
                insurance = insurance_item.__dict__
                get_insurance = dict()
                get_insurance['insurance_code'] = insurance['ec_code']
                get_insurance['insurance_name'] = insurance['name']
                get_insurance['insurance_telephone'] = insurance['service_telephone']
                get_insurance['insurance_claim_type'] = insurance['claim_type']
                payment = str(insurance['claim_payment_per_count'])
                if payment != "0":
                    payment_str = "{}만원".format(payment[:-4])
                else:
                    payment_str = "-"
                get_insurance['insurance_per_max_payment'] = payment_str
                set_essential_item_list.append(dict(insurant_work_flag=insurance['insurant_work_flag'],
                                                    beneficiary_work_flag=insurance['beneficiary_work_flag']))
                get_insurance['essential_input_info'] = set_essential_item_list
                del set_essential_item_list
                set_insurance_list.append(get_insurance)

            return response_message_handler(200, result_detail=set_insurance_list)
        else:
            return response_message_handler(204)

    except Exception as error:
        logger.critical(error, exc_info=True)
        return response_message_handler(500)

    finally:
        db.close()
        gc.collect()


"""

전체 은행 목록 조회하기

"""


def get_bank_company_list(data, header):
    db = SessionLocal()

    try:
        set_bank_list = []
        logger.info("header : {}".format(header))
        logger.info("data : {}".format(data))

        if 'bank_code' in data and data['bank_code'] != '':
            bank_info = db.query(BankClass).filter_by(ec_code=data['bank_code']).order_by(BankClass.order,
                                                                                          BankClass.name)

            if bank_info.count() > 0:
                bank = bank_info.first().__dict__
                get_bank = dict()
                get_bank['bank_code'] = bank['ec_code']
                get_bank['bank_name'] = bank['name']
                set_bank_list.append(get_bank)
            else:
                return response_message_handler(204)

        else:

            # 은행이름은 ㄱ-ㅎ , a-z 순으로 정렬
            bank_list = db.query(BankClass).order_by(BankClass.order, BankClass.name).all()

            if bank_list:

                for bank_info in bank_list:
                    get_bank = dict()
                    bank = bank_info.__dict__
                    del bank['_sa_instance_state']

                    get_bank['bank_code'] = bank['ec_code']
                    get_bank['bank_name'] = bank['name']
                    set_bank_list.append(get_bank)

            else:
                return response_message_handler(204)

        return response_message_handler(200, result_detail=set_bank_list)

    except Exception as error:
        logger.critical(error, exc_info=True)
        return response_message_handler(500)

    finally:
        db.close()
        gc.collect()


"""

병원 정보 조회하기

"""


def get_hospital_info(data, header):
    db = SessionLocal()

    try:

        logger.info("header : {}".format(header))
        logger.info("data : {}".format(data))

        set_hospital_info = dict()
        set_treat_department_list = []

        week_day_list = ["일", "월", "화", "수", "목", "금", "토"]

        partner_info = db.query(PartnerClass).filter_by(partner_auth_token=header['Auth-Token'])

        # 파라미터를 통해 불러오는 파트너사 정보가 없다면, 기본 hospital_seq의 파트너사 정보를 불러온다.
        if partner_info.count() > 0:

            get_partner_info = partner_info.first().__dict__
            hospital_seq = get_partner_info['hospital_seq']
            set_hospital_info['name'] = get_partner_info['partner_name']
            set_hospital_info['address'] = get_partner_info['partner_address']
            set_hospital_info['logo_image_url'] = get_partner_info['logo_image_url']

            set_hospital_week_day = ''

            if get_partner_info['active_week'] != '':
                get_active_week_list = get_partner_info['active_week'].split(",")
                for index, get_active_week in enumerate(get_active_week_list):
                    if get_active_week == "1":
                        set_hospital_week_day += week_day_list[index] + ","

            if ',' in set_hospital_week_day:

                set_hospital_info['active_week_day'] = set_hospital_week_day[:-1]
            else:
                set_hospital_info['active_week_day'] = set_hospital_week_day

            get_active_time = get_partner_info['active_time']

            if get_active_time != '':

                if ',' in get_active_time:
                    get_active_time = get_active_time.replace(',', '~')

            set_hospital_info['active_time'] = get_active_time

            treat_department_list = db.query(TreatClass).filter_by(hospital_seq=hospital_seq).order_by(
                TreatClass.order, TreatClass.name)

            if treat_department_list.count() > 0:

                for treat_department in treat_department_list:
                    treat_department = treat_department.__dict__
                    get_treat_department = dict()
                    get_treat_department['treat_department_code'] = treat_department['ec_code']
                    get_treat_department['treat_department_name'] = treat_department['name']
                    set_treat_department_list.append(get_treat_department)
                    del get_treat_department
            else:

                treat_department_list = db.query(TreatClass).filter_by(
                    hospital_seq=default_hospital_seq).order_by(TreatClass.order,
                                                                TreatClass.name)

                for treat_department in treat_department_list:
                    treat_department = treat_department.__dict__
                    get_treat_department = dict()
                    get_treat_department['treat_department_code'] = treat_department['ec_code']
                    get_treat_department['treat_department_name'] = treat_department['name']

                    set_treat_department_list.append(get_treat_department)
                    del get_treat_department

            set_hospital_info['treat_department_list'] = set_treat_department_list

            del treat_department_list
            del partner_info

            return response_message_handler(200, result_detail=set_hospital_info)
        else:
            return response_message_handler(401)
    except Exception as error:
        logger.critical(error, exc_info=True)
        return response_message_handler(500)

    finally:
        db.close()
        gc.collect()

"""

직업 정보 조회하기

"""


def get_work_list(data, header):
    db = SessionLocal()

    result = []

    try:

        work_list = db.query(WorkClass).filter_by(active=1).order_by(WorkClass.code.asc()).all()

        if len(work_list) > 0:

            for work_item in work_list:
                get_work_item = work_item.__dict__
                result.append(dict(code=get_work_item['code'],
                                   name=get_work_item['name']))

            del work_list
            return response_message_handler(200, result_detail=result)
        else:

            return response_message_handler(204)

    except Exception as error:
        logger.critical(error, exc_info=True)
        return response_message_handler(500)

    finally:
        db.close()
        gc.collect()