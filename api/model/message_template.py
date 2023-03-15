"""

메시지 템플릿 클래스 입니다

"""
from re import ASCII

from sqlalchemy import Column, BigInteger, NVARCHAR, case, Text
from sqlalchemy.ext.hybrid import hybrid_property

from api import Base


class MessageTemplateClass(Base):
    __tablename__ = "ec_message_template"
    __table_args__ = {"extend_existing": True}

    seq = Column(BigInteger, autoincrement=True, primary_key=True)
    template_id = Column(NVARCHAR(length=100), nullable=False, default="")
    send_type = Column(NVARCHAR(length=10), nullable=False, default="")
    message = Column(Text, nullable=False, default="")
    create_date = Column(BigInteger, nullable=False, default=0)
    update_date = Column(BigInteger, nullable=False, default=0)

    def __str__(self):
        print('MessageTemplateClass toString : {}'.format(self.__dict__))
