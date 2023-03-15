
from sqlalchemy import Column, BigInteger, NVARCHAR, Boolean

from api import Base


class DistrictSidoClass(Base):
    __tablename__ = "ec_district_sido"
    __table_args__ = {"extend_existing": True}

    seq = Column(BigInteger, autoincrement=True, primary_key=True)
    code = Column(BigInteger, nullable=False, default=0)
    name = Column(NVARCHAR(length=100), nullable=False, default="")
    active = Column(Boolean, nullable=False, default=True)

    def __str__(self):
        print('DistrictSidoCategoryClass toString : {}'.format(self.__dict__))
