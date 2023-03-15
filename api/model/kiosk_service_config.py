
from sqlalchemy import Column, BigInteger, NVARCHAR, TEXT, Integer

from api import Base


class KioskServiceConfigClass(Base):
    __tablename__ = "ec_kiosk_service_config"
    __table_args__ = {"extend_existing": True}

    seq = Column(BigInteger, autoincrement=True, primary_key=True)
    service_seq = Column(BigInteger, autoincrement=False, default=0)
    service_version = Column(NVARCHAR(length=10), nullable=False, default="")
    config = Column(TEXT, autoincrement=False, default="")
    active = Column(Integer, autoincrement=False, default="")
    create_date = Column(BigInteger, nullable=False, default=0)
    update_date = Column(BigInteger, nullable=False, default=0)

    def __str__(self):
        print('KioskServiceConfigClass toString : {}'.format(self.__dict__))
