"""

개인정보 이용동의 클래스

"""
from sqlalchemy import Column, BigInteger, TEXT, NVARCHAR, Boolean, Integer

from api import Base


class TermsClass(Base):
    __tablename__ = "ec_terms"
    __table_args__ = {"extend_existing": True}

    seq = Column(BigInteger, autoincrement=True, primary_key=True)
    order = Column(Integer, nullable=False, default=0)
    agree_type = Column(NVARCHAR(length=20), nullable=False, default="")
    service_type = Column(NVARCHAR(length=20), nullable=False, default="")
    ec_partner_code = Column(NVARCHAR(length=200), nullable=False, default="")
    is_need_agree = Column(Boolean, nullable=False, default=False)
    name = Column(NVARCHAR(length=200), nullable=False, default="")
    information = Column(TEXT, nullable=False, default="")
    create_date = Column(BigInteger, nullable=False, default=0)
    update_date = Column(BigInteger, nullable=False, default=0)

    def __str__(self):
        print('TermsClass toString : {}'.format(self.__dict__))
