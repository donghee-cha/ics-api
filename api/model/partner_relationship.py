"""

파트너사 연결정보 테이블입니다.

"""

from sqlalchemy import Column, BigInteger, NVARCHAR, Integer, TEXT, Boolean

from api import Base


class PartnerRelationshipClass(Base):
    __tablename__ = "ec_partner_relationship"
    __table_args__ = {"extend_existing": True}

    seq = Column(BigInteger, autoincrement=True, primary_key=True)
    partner_code = Column(NVARCHAR(length=200), autoincrement=False, default="")
    workspace_partner_code = Column(NVARCHAR(length=200), autoincrement=False, default="")
    active = Column(Boolean, nullable=False, default=True)
    create_date = Column(BigInteger, nullable=False, default=0)
    update_date = Column(BigInteger, nullable=False, default=0)

    def __str__(self):
        print('PartnerRelationshipClass toString : {}'.format(self.__dict__))
