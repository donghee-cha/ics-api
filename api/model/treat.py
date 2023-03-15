"""

ICS 에서 사용하는 진료과 정보 클래스 입니다

"""

from sqlalchemy import Column, BigInteger, NVARCHAR, Integer

from api import Base


class TreatClass(Base):
    __tablename__ = "ec_treat"
    __table_args__ = {"extend_existing": True}

    seq = Column(BigInteger, autoincrement=True, primary_key=True)
    ec_hospital_code = Column(NVARCHAR(length=200), nullable=False, default="")
    order = Column(Integer, nullable=False, default=0)
    hospital_seq = Column(BigInteger, nullable=False, default=0)
    ec_code = Column(NVARCHAR(length=200), nullable=False, default="")
    name = Column(NVARCHAR(length=200), autoincrement=False, default="")
    create_date = Column(BigInteger, nullable=False, default=0)
    update_date = Column(BigInteger, nullable=False, default=0)

    def __str__(self):
        print('TreatClass toString : {}'.format(self.__dict__))
