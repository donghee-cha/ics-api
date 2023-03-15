
from sqlalchemy import Column, BigInteger, NVARCHAR, TEXT, Integer

from api import Base


class StatisticPrintCountData(Base):
    __tablename__ = "statistic_print_count_data"
    __table_args__ = {"extend_existing": True}

    seq = Column(BigInteger, autoincrement=True, primary_key=True)
    partner_code = Column(NVARCHAR(length=200), autoincrement=False, default="")
    device_code = Column(NVARCHAR(length=200), nullable=False, default="")
    service_type = Column(Integer, nullable=False, default=0)
    history_id = Column(NVARCHAR(length=200), nullable=False, default="")
    document_code = Column(NVARCHAR(length=100), nullable=False, default="")
    print_count = Column(Integer, nullable=False, default=0)
    file_count = Column(Integer, nullable=False, default=0)
    count_date = Column(BigInteger, nullable=False, default=0)
    create_date = Column(BigInteger, nullable=False, default=0)

    def __str__(self):
        print('KioskServiceStatusLog toString : {}'.format(self.__dict__))
