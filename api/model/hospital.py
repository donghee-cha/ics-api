
from sqlalchemy import Column, BigInteger, NVARCHAR, TEXT, Integer

from api import Base


class HospitalClass(Base):
    __tablename__ = "ec_hospital"
    __table_args__ = {"extend_existing": True}

    seq = Column(BigInteger, autoincrement=True, primary_key=True)
    treat_type = Column(Integer, nullable=False, default=10)
    code = Column(NVARCHAR(length=20), nullable=False, default="")
    external_name = Column(NVARCHAR(length=200), nullable=False, default="")
    name = Column(NVARCHAR(length=200), nullable=False, default="")
    address = Column(TEXT, nullable=False, default="")
    zip_code = Column(NVARCHAR(length=100), nullable=False, default="")
    is_dbinsu = Column(Integer, nullable=False, default=0)
    active = Column(Integer, nullable=False, default=1)
    create_date = Column(BigInteger, nullable=False, default=0)
    update_date = Column(BigInteger, nullable=False, default=0)

    def __str__(self):
        print('HospitalClass toString : {}'.format(self.__dict__))
