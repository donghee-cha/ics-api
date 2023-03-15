"""

ICS 에서 사용하는 디바이스 정보 클래스 입니다.

"""

from sqlalchemy import Column, BigInteger, NVARCHAR, TEXT, Boolean

from api import Base


class KioskClass(Base):
    __tablename__ = "ec_kiosk"
    __table_args__ = {"extend_existing": True}

    seq = Column(BigInteger, autoincrement=True, primary_key=True)
    active = Column(Boolean, nullable=False, default=1)
    ec_partner_code = Column(NVARCHAR(length=200), nullable=False, default="")
    ec_kiosk_model_seq = Column(BigInteger, autoincrement=False, default=0)
    code = Column(NVARCHAR(length=200), autoincrement=False, default="")
    namespace = Column(NVARCHAR(length=100), autoincrement=False, default="")
    location = Column(TEXT, autoincrement=False, default="")
    status = Column(NVARCHAR(length=20), autoincrement=False, default="")
    installed_date = Column(BigInteger, autoincrement=False, default=0)
    installer_name = Column(NVARCHAR(length=20), autoincrement=False, default="")
    program_version_date = Column(BigInteger, autoincrement=False, default=0)
    program_version = Column(NVARCHAR(length=200), autoincrement=False, default="")
    program_download_url = Column(TEXT, autoincrement=False, default="")
    memo = Column(TEXT, autoincrement=False, default="")
    create_date = Column(BigInteger, nullable=False, default=0)
    update_date = Column(BigInteger, nullable=False, default=0)

    def __str__(self):
        print('KioskClass toString : {}'.format(self.__dict__))
