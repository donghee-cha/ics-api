

from sqlalchemy import Column, BigInteger, NVARCHAR, Integer, TEXT, Boolean

from api import Base


class SignageStorageClass(Base):
    __tablename__ = "ec_signage_storage"
    __table_args__ = {"extend_existing": True}

    seq = Column(BigInteger, autoincrement=True, primary_key=True)
    status = Column(Boolean, nullable=False, default=False)
    active = Column(Boolean, nullable=False, default=True)
    is_static = Column(Boolean, nullable=False, default=True)
    origin_seq = Column(BigInteger, nullable=False, default=1)
    content_type = Column(NVARCHAR(length=100), nullable=False, default="")
    file_name = Column(TEXT, nullable=False, default="")
    close_date = Column(BigInteger, nullable=False, default=0)
    output_time = Column(Integer, nullable=False, default=0)
    create_date = Column(BigInteger, nullable=False, default=0)
    update_date = Column(BigInteger, nullable=False, default=0)

    def __str__(self):
        print('SignageStorageClass toString : {}'.format(self.__dict__))
