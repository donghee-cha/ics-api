"""

ICS 에서 사용하는 고객사정보 클래스 입니다

"""

from sqlalchemy import Column, BigInteger, NVARCHAR, Integer, TEXT, Boolean

from api import Base


class SignageClass(Base):
    __tablename__ = "ec_signage"
    __table_args__ = {"extend_existing": True}

    seq = Column(BigInteger, autoincrement=True, primary_key=True)
    active = Column(Boolean, autoincrement=False, default=True)
    ec_partner_code = Column(NVARCHAR(length=200), nullable=False, default="")
    signage_version = Column(NVARCHAR(length=200), nullable=False, default="")
    signage_date = Column(BigInteger, nullable=False, default=0)
    signage_url_information = Column(TEXT, nullable=False, default="")
    create_date = Column(BigInteger, nullable=False, default=0)
    update_date = Column(BigInteger, nullable=False, default=0)

    def __str__(self):
        print('PartnerICSConfigClass toString : {}'.format(self.__dict__))
