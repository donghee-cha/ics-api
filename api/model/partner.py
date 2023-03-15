"""

ICS 에서 사용하는 고객사정보 클래스 입니다

"""

from sqlalchemy import Column, BigInteger, NVARCHAR, Integer, TEXT, Boolean

from api import Base


class PartnerClass(Base):
    __tablename__ = "ec_partner"
    __table_args__ = {"extend_existing": True}

    seq = Column(BigInteger, autoincrement=True, primary_key=True)
    partner_group_code = Column(NVARCHAR(length=100), nullable=False, default="")
    partner_code = Column(NVARCHAR(length=200), autoincrement=False, default="")
    emr_code = Column(NVARCHAR(length=200), autoincrement=False, default="")
    hospital_code = Column(NVARCHAR(length=200), autoincrement=False, default="")
    hospital_seq = Column(BigInteger, autoincrement=False, default=0)
    partner_secret_key = Column(NVARCHAR(length=200), autoincrement=False, default="")
    partner_auth_token = Column(NVARCHAR(length=200), autoincrement=False, default="")
    partner_name = Column(NVARCHAR(length=200), nullable=False, default="")
    partner_address = Column(TEXT, nullable=False, default="")
    partner_main_location = Column(NVARCHAR(50), nullable=False, default="")
    logo_image_url = Column(TEXT, nullable=False, default="")
    active_week = Column(NVARCHAR(length=20), nullable=False, default="")
    active_time = Column(NVARCHAR(length=20), nullable=False, default="")
    partner_admin_id = Column(NVARCHAR(length=20), nullable=False, default="")
    partner_admin_password = Column(NVARCHAR(length=100), nullable=False, default="")
    plugin_information = Column(TEXT, nullable=False, default="")
    plugin_config_seq = Column(BigInteger, nullable=False, default=0)
    send_notification_type = Column(Integer, nullable=False, default=20)
    active = Column(Boolean, nullable=False, default=True)
    host = Column(TEXT, autoincrement=False, default="")
    create_date = Column(BigInteger, nullable=False, default=0)
    update_date = Column(BigInteger, nullable=False, default=0)

    def __str__(self):
        print('PartnerClass toString : {}'.format(self.__dict__))
