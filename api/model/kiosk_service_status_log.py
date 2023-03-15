
from sqlalchemy import Column, BigInteger, NVARCHAR, TEXT, Integer

from api import Base


class KioskServiceStatusLog(Base):
    __tablename__ = "ec_kiosk_service_status_log"
    __table_args__ = {"extend_existing": True}

    seq = Column(BigInteger, autoincrement=True, primary_key=True)
    ec_partner_code = Column(NVARCHAR(length=200), nullable=False, default='')
    device_code = Column(NVARCHAR(length=20), nullable=False, default="")
    status_check_time = Column(BigInteger, nullable=False, default=0)
    status_message = Column(TEXT, nullable=False, default="")
    create_date = Column(BigInteger, nullable=False, default=0)

    def __str__(self):
        print('KioskServiceStatusLog toString : {}'.format(self.__dict__))
