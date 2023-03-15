"""

ICS 에서 사용하는 알림톡발송 클래스 입니다

"""

from sqlalchemy import Column, BigInteger, Integer, TEXT, NVARCHAR, Boolean

from api import Base


class ClaimSendLog(Base):
    __tablename__ = "ec_claim_send_log"
    __table_args__ = {"extend_existing": True}

    seq = Column(BigInteger, autoincrement=True, primary_key=True)
    claim_id = Column(NVARCHAR(length=200), nullable=False, default="")
    ec_insurance_code = Column(NVARCHAR(length=200), nullable=False, default="")
    send_document_count = Column(Integer, nullable=False, default=0)
    send_type = Column(Integer, nullable=False, default=1)
    send_date = Column(BigInteger, nullable=False, default=0)
    send_plugin = Column(NVARCHAR(length=200), nullable=False, default="")
    send_plugin_id = Column(Integer, nullable=False, default=0)
    is_send_success = Column(Boolean, nullable=False, default=False)
    receive_date = Column(BigInteger, nullable=False, default=0)
    description = Column(TEXT, nullable=False, default="")
    create_date = Column(BigInteger, nullable=False, default=0)

    def __str__(self):
        print('ClaimSendLog toString : {}'.format(self.__dict__))
