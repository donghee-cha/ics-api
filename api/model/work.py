"""

직업 정보 클래스

"""
from sqlalchemy import Column, BigInteger, Integer , NVARCHAR, Boolean

from api import Base


class WorkClass(Base):
    __tablename__ = "ec_work"
    __table_args__ = {"extend_existing": True}

    seq = Column(BigInteger, autoincrement=True, primary_key=True)
    code = Column(Integer, nullable=False, default=0)
    name = Column(NVARCHAR(length=200), nullable=False, default="")
    active = Column(Boolean, nullable=False, default=False)
    create_date = Column(BigInteger, nullable=False, default=0)
    update_date = Column(BigInteger, nullable=False, default=0)

    def __str__(self):
        print('WorkClass toString : {}'.format(self.__dict__))

