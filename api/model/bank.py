"""

ICS 에서 사용하는 은행정보 클래스 입니다

"""
from re import ASCII

from sqlalchemy import Column, BigInteger, NVARCHAR, case, Integer
from sqlalchemy.ext.hybrid import hybrid_property

from api import Base


class BankClass(Base):
    __tablename__ = "ec_bank"
    __table_args__ = {"extend_existing": True}

    seq = Column(BigInteger, autoincrement=True, primary_key=True)
    order = Column(Integer, nullable=False, default=0)
    ec_code = Column(NVARCHAR(length=200), nullable=False, default="")
    name = Column(NVARCHAR(length=100), nullable=False, default="")
    create_date = Column(BigInteger, nullable=False, default=0)
    update_date = Column(BigInteger, nullable=False, default=0)

    def __str__(self):
        print('BankClass toString : {}'.format(self.__dict__))

    @hybrid_property
    def difficulty(cls):
        # this expression is used when querying the model
        return case(
            [(ASCII(cls.name[1]) < 123), 2],
            else_=1
        )