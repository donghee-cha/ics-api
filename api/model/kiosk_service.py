
from sqlalchemy import Column, BigInteger, NVARCHAR, TEXT, Integer, Text

from api import Base


class KioskServiceClass(Base):
    __tablename__ = "ec_kiosk_service"
    __table_args__ = {"extend_existing": True}

    seq = Column(BigInteger, autoincrement=True, primary_key=True)
    device_code = Column(NVARCHAR(length=20), nullable=False, default="")
    ec_partner_code = Column(NVARCHAR(length=200), nullable=False, default="")
    ec_kiosk_model_seq = Column(BigInteger, nullable=False, default=0)
    ec_emr_company_seq = Column(BigInteger, nullable=False, default=0)
    service_seq = Column(BigInteger, nullable=False, default=0)
    service_version = Column(NVARCHAR(length=10), nullable=False, default="")
    service_download_url = Column(NVARCHAR(length=500), nullable=False, default="")
    service_config = Column(Text, nullable=False, default="")
    service_version_update_date = Column(BigInteger, nullable=False, default=0)
    os = Column(NVARCHAR(length=20), nullable=False, default="")
    os_wakeup_time = Column(NVARCHAR(length=10), nullable=False, default="")
    os_sleep_time = Column(NVARCHAR(length=10), nullable=False, default="")
    network = Column(NVARCHAR(length=10), nullable=False, default="")
    location = Column(TEXT, nullable=False, default="")
    installed_date = Column(BigInteger, nullable=False, default=0)
    installer_seq = Column(BigInteger, nullable=False, default=0)
    signage_flag = Column(Integer, nullable=False, default=0)
    printer_flag = Column(Integer, nullable=False, default=0)
    memo = Column(TEXT, nullable=False, default="")
    status = Column(Integer, nullable=False, default=100)
    active = Column(Integer, nullable=False, default="")
    create_date = Column(BigInteger, nullable=False, default=0)
    update_date = Column(BigInteger, nullable=False, default=0)

    def __str__(self):
        print('KioskServiceClass toString : {}'.format(self.__dict__))
