"""

보험사 정보 클래스

"""
from sqlalchemy import Column, BigInteger, Integer, TEXT, NVARCHAR, Boolean

from api import Base


class InsuranceClass(Base):
    __tablename__ = "ec_insurance"
    __table_args__ = {"extend_existing": True}

    seq = Column(BigInteger, autoincrement=True, primary_key=True)
    ec_code = Column(NVARCHAR(length=200), nullable=False, default="")
    order = Column(Integer, nullable=False, default=1)
    name = Column(NVARCHAR(length=50), nullable=False, default="")
    service_telephone = Column(NVARCHAR(length=50), nullable=False, default="")
    post_office_location = Column(NVARCHAR(length=50), nullable=False, default="")
    fax_number = Column(NVARCHAR(length=100), nullable=False, default="")
    email = Column(NVARCHAR(length=100), nullable=False, default="")
    logo_image_url = Column(TEXT, nullable=False, default="")
    terms_information = Column(TEXT, nullable=False, default="")
    claim_type = Column(Integer, nullable=False, default=0)
    claim_description = Column(TEXT, nullable=False, default="")
    claim_payment_per_count = Column(Integer, nullable=False, default=0)
    claim_template_image_url = Column(TEXT, nullable=False, default="")
    active = Column(Boolean, nullable=False, default=False)
    insurant_work_flag = Column(Boolean, nullable=False, default=False)
    beneficiary_work_flag = Column(Boolean, nullable=False, default=False)
    create_date = Column(BigInteger, nullable=False, default=0)
    update_date = Column(BigInteger, nullable=False, default=0)

    def __str__(self):
        print('InsuranceClass toString : {}'.format(self.__dict__))
