"""

제3자 서비스 이용약관 동의

"""
from sqlalchemy import Column, BigInteger, TEXT, NVARCHAR, Integer

from api import Base


class ThirdPartyTermsClass(Base):
    __tablename__ = "ec_thirdparty_terms"
    __table_args__ = {"extend_existing": True}

    seq = Column(BigInteger, autoincrement=True, primary_key=True)
    thirdparty_name = Column(NVARCHAR(length=200), nullable=False, default="")
    thirdparty_type = Column(NVARCHAR(length=200), nullable=False, default="")
    is_need_agree = Column(Integer, nullable=False, default=1)
    name = Column(NVARCHAR(length=200), nullable=False, default="")
    information = Column(TEXT, nullable=False, default="")
    create_date = Column(BigInteger, nullable=False, default=0)
    update_date = Column(BigInteger, nullable=False, default=0)

    def __str__(self):
        print('ThirdPartyTerms toString : {}'.format(self.__dict__))
