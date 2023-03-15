from sqlalchemy import Column, BigInteger, NVARCHAR, Boolean, Text, Integer

from api import Base


class BenefitClass(Base):
    __tablename__ = "ec_benefit"
    __table_args__ = {"extend_existing": True}

    seq = Column(BigInteger, autoincrement=True, primary_key=True)
    code = Column(NVARCHAR(length=20), nullable=False, default='')
    name = Column(NVARCHAR(length=100), nullable=False, default='')
    category = Column(NVARCHAR(length=20), nullable=False, default='')
    description = Column(Text, nullable=False, default='')
    partner_code = Column(BigInteger, nullable=False, default=0)
    usage_partner_code = Column(Text, nullable=False, default='')
    partner_product_code = Column(NVARCHAR(length=20), nullable=False, default='')
    partner_product_name = Column(NVARCHAR(length=100), nullable=False, default='')
    terms_information = Column(Text, nullable=False, default='')
    notice_description = Column(Text, nullable=False, default='')
    kiosk_list_banner_file_name = Column(NVARCHAR(length=500), nullable=False, default='')
    kiosk_view_information = Column(Text, nullable=False, default='')
    web_list_banner_file_name = Column(NVARCHAR(length=500), nullable=False, default='')
    web_view_information = Column(Text, nullable=False, default='')
    complete_view_file_name = Column(NVARCHAR(length=500), nullable=False, default='')
    complete_web_view_file_name = Column(NVARCHAR(length=500), nullable=False, default='')
    share_url = Column(NVARCHAR(length=500), nullable=False, default='')
    web_url = Column(NVARCHAR(length=500), nullable=False, default='')
    product_url = Column(NVARCHAR(length=500), nullable=False, default='')
    send_message_template = Column(NVARCHAR(length=20), nullable=False, default='')
    send_applicant_message_template = Column(NVARCHAR(length=20), nullable=False, default='')
    start_date = Column(BigInteger, nullable=False, default=0)
    end_date = Column(BigInteger, nullable=False, default=0)
    recommender_flag = Column(Integer, nullable=False, default=0)
    active = Column(Boolean, nullable=False, default=1)
    memo = Column(Text, nullable=False, default='')
    create_date = Column(BigInteger, nullable=False, default=0)
    update_date = Column(BigInteger, nullable=False, default=0)
