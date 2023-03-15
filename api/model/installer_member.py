
from sqlalchemy import Column, BigInteger, NVARCHAR, Integer

from api import Base


class InstallerMemberClass(Base):
    __tablename__ = "ec_installer_member"
    __table_args__ = {"extend_existing": True}

    seq = Column(BigInteger, autoincrement=True, primary_key=True)
    name = Column(NVARCHAR(length=100), nullable=False, default="")
    cellphone = Column(NVARCHAR(length=20), nullable=False, default="")
    active = Column(Integer, autoincrement=False, default=1)
    create_date = Column(BigInteger, nullable=False, default=0)
    update_date = Column(BigInteger, nullable=False, default=0)

    def __str__(self):
        print('KioskClass toString : {}'.format(self.__dict__))
