from sqlalchemy import Column, BigInteger, NVARCHAR, Boolean, Text

from api import Base


class BenefitApplicationClass(Base):
    __tablename__ = "ec_benefit_applicant"
    __table_args__ = {"extend_existing": True}

    seq = Column(BigInteger, autoincrement=True, primary_key=True)
    benefit_code = Column(NVARCHAR(length=20), nullable=False, default="")
    device_code = Column(NVARCHAR(length=200), nullable=False, default="")
    device_use_date = Column(BigInteger, nullable=False, default=0)
    applicant_id = Column(NVARCHAR(length=100), nullable=False, default="")
    applicant_name = Column(NVARCHAR(length=100), nullable=False, default="")
    applicant_cellphone = Column(NVARCHAR(length=200), nullable=False, default="")
    hospital_name = Column(NVARCHAR(length=200), nullable=False, default="")
    hospital_code = Column(NVARCHAR(length=20), nullable=False, default="")
    district_sido_code = Column(BigInteger, nullable=False, default=0)
    district_sido_name = Column(NVARCHAR(length=100), nullable=False, default="")
    district_sigungu_code = Column(BigInteger, nullable=False, default=0)
    district_sigungu_name = Column(NVARCHAR(length=100), nullable=False, default="")
    partner_code = Column(NVARCHAR(length=200), nullable=False, default="")
    partner_recommender = Column(NVARCHAR(length=100), nullable=False, default="")
    birthday_year = Column(NVARCHAR(length=200), nullable=False, default="")
    gender = Column(NVARCHAR(length=200), nullable=False, default="")
    create_date = Column(BigInteger, nullable=False, default=0)
