"""

ICS 에서 사용하는 이용자 클래스 입니다

"""

from sqlalchemy import Column, BigInteger, Integer, TEXT, NVARCHAR, Boolean

from api import Base


class ClaimClass(Base):
    __tablename__ = "ec_claim_history_dev"
    __table_args__ = {"extend_existing": True}

    seq = Column(BigInteger, autoincrement=True, primary_key=True)
    device = Column(NVARCHAR(length=200), nullable=False, default="")
    claim_id = Column(NVARCHAR(length=200), nullable=False, default="")
    ec_partner_code = Column(NVARCHAR(length=20), nullable=False, default="")
    ec_partner_auth_token = Column(NVARCHAR(length=200), nullable=False, default="")
    ec_insurance_code_list = Column(TEXT, nullable=False, default="")
    personal_fax_number_list = Column(TEXT, nullable=False, default="")
    # 0: 본인임, 1: 본인이 아님
    insurant_type = Column(Integer, nullable=False, default=0)
    # 0: 통원, 1: 입원, 2: 골절, 3: 수술, 4: 장해, 5: 진단, 6: 사고/재해
    claim_type = Column(Integer, nullable=False, default=0)
    # 0:질병, 1:사고, 2: 교통사고
    accident_type = Column(Integer, nullable=False, default=0)
    accident_date = Column(BigInteger, nullable=False, default=0)
    treat_code = Column(NVARCHAR(length=100), nullable=False, default="")
    diagnosis_name = Column(NVARCHAR(length=200), nullable=False, default="")
    insurant_name = Column(NVARCHAR(length=100), nullable=False, default="")
    insurant_cellphone = Column(NVARCHAR(length=200), nullable=False, default="")
    is_uploaded_insurant_signature = Column(Boolean, nullable=False, default=False)
    insurant_identify_number = Column(NVARCHAR(length=200), nullable=False, default="")
    is_need_protect = Column(Boolean, nullable=False, default=False)
    beneficiary_relationship_type = Column(Integer, nullable=False, default=0)
    beneficiary_name = Column(NVARCHAR(length=100), nullable=False, default="")
    beneficiary_cellphone = Column(NVARCHAR(length=200), nullable=False, default="")
    beneficiary_identify_number = Column(NVARCHAR(length=200), nullable=False, default="")
    is_uploaded_beneficiary_signature = Column(Boolean, nullable=False, default=False)
    bank_code = Column(NVARCHAR(length=200), nullable=False, default="")
    bank_account_number = Column(NVARCHAR(length=100), nullable=False, default="")
    bank_account_name = Column(NVARCHAR(length=100), nullable=False, default="")
    insurance_type = Column(Integer, nullable=False, default=1)
    insurance_request_status = Column(Integer, nullable=False, default=0)
    insurance_request_date = Column(BigInteger, nullable=False, default=0)
    claim_status = Column(Integer, nullable=False, default=0)
    claim_date = Column(BigInteger, nullable=False, default=0)
    terms_description = Column(TEXT, nullable=False, default="")
    terms_third_party_agree = Column(NVARCHAR(length=5), nullable=False, default="")
    terms_marketing_agree = Column(NVARCHAR(length=5), nullable=False, default="")
    documentary_submit_status = Column(Integer, nullable=False, default=0)
    is_uploaded_documentary = Column(Boolean, nullable=False, default=False)
    active = Column(Boolean, nullable=False, default=True)
    age = Column(Integer, nullable=False, default=0)
    gender = Column(NVARCHAR(length=5), nullable=False, default="")
    insurant_work_code = Column(Integer, nullable=False, default=0)
    insurant_work_etc = Column(NVARCHAR(length=200), nullable=False, default='')
    insurant_workplace = Column(TEXT, nullable=False, default='')
    beneficiary_work_code = Column(Integer, nullable=False, default=0)
    beneficiary_work_etc = Column(NVARCHAR(length=200), nullable=False, default='')
    beneficiary_workplace = Column(TEXT, nullable=False, default='')
    create_date = Column(BigInteger, nullable=False, default=0)
    update_date = Column(BigInteger, nullable=False, default=0)

    def __str__(self):
        print('ClaimClass toString : {}'.format(self.__dict__))
