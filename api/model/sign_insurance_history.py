from sqlalchemy import Column, BigInteger, NVARCHAR, TEXT, BOOLEAN
from sqlalchemy.dialects.mysql import LONGTEXT

from api import Base


class SignInsuranceHistoryClass(Base):
    __tablename__ = "ec_sign_insurance_history"
    __table_args__ = {"extend_existing": True}

    seq = Column(BigInteger, autoincrement=True, primary_key=True)
    device_code = Column(NVARCHAR(length=200), nullable=False, default="")
    name = Column(NVARCHAR(length=100), nullable=False, default="")
    cellphone = Column(NVARCHAR(length=200), nullable=False, default="")
    birthday = Column(NVARCHAR(length=100), nullable=False, default="")
    insurance_information = Column(LONGTEXT, nullable=False, default="")
    insurance_document_request_agree = Column(NVARCHAR(length=5), nullable=False, default="")
    insurance_coverage_case = Column(TEXT, nullable=False, default="")
    active = Column(BOOLEAN, nullable=False, default=1)
    create_date = Column(BigInteger, nullable=False, default=0)
