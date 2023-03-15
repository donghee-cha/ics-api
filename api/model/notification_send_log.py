"""

ICS 에서 사용하는 알림톡 히스토리 정보 클래스 입니다

"""

from sqlalchemy import Column, BigInteger, Integer, TEXT, NVARCHAR, Boolean

from api import Base


class NotificationSendLog(Base):
    __tablename__ = "ec_notification_send_log"
    __table_args__ = {"extend_existing": True}

    seq = Column(BigInteger, autoincrement=True, primary_key=True)
    is_batch = Column(Boolean, nullable=False, default=False)
    claim_id = Column(NVARCHAR(length=200), nullable=False, default="")
    type = Column(Integer, nullable=False, default=0)
    message_template_seq = Column(BigInteger, nullable=False, default=0)
    send_message = Column(TEXT, nullable=False, default="")
    message = Column(TEXT, nullable=False, default="")
    is_send_success = Column(Boolean, nullable=False, default=0)
    status = Column(Boolean, nullable=False, default=1)
    send_date = Column(BigInteger, nullable=False, default=0)
    send_reservation_date = Column(BigInteger, nullable=False, default=0)
    create_date = Column(BigInteger, nullable=False, default=0)
    update_date = Column(BigInteger, nullable=False, default=0)

    def __str__(self):
        print('NotificationSendLog toString : {}'.format(self.__dict__))
