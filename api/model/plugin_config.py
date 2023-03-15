
from sqlalchemy import Column, BigInteger, Integer, TEXT, NVARCHAR, Boolean

from api import Base


class PluginConfigClass(Base):
    __tablename__ = "ec_plugin_config"
    __table_args__ = {"extend_existing": True}

    seq = Column(BigInteger, autoincrement=True, primary_key=True)
    active = Column(Boolean, nullable=False, default=True)
    s3_region = Column(NVARCHAR(length=200), nullable=False, default="")
    s3_access_key = Column(TEXT, nullable=False, default="")
    s3_secret_key = Column(TEXT, nullable=False, default="")
    s3_bucket = Column(NVARCHAR(length=200), nullable=False, default="")
    create_date = Column(BigInteger, nullable=False, default=0)
    update_date = Column(BigInteger, nullable=False, default=0)

    def __str__(self):
        print('PluginConfigClass toString : {}'.format(self.__dict__))
