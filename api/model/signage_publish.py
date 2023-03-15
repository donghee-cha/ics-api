
from sqlalchemy import Column, BigInteger, NVARCHAR, Integer, TEXT, Boolean

from api import Base


class SignagePublishClass(Base):
    __tablename__ = "ec_signage_publish"
    __table_args__ = {"extend_existing": True}

    seq = Column(BigInteger, autoincrement=True, primary_key=True)
    active = Column(Boolean, autoincrement=False, default=True)
    partner_code = Column(NVARCHAR(length=200), nullable=False, default="")
    signage_publish_number = Column(Integer, nullable=False, default=1)
    file_name = Column(TEXT, nullable=False, default="")
    signage_storage_seq_list = Column(TEXT, nullable=False, default="")
    create_date = Column(BigInteger, nullable=False, default=0)
    update_date = Column(BigInteger, nullable=False, default=0)

    def __str__(self):
        print('SignagePublishClass toString : {}'.format(self.__dict__))
