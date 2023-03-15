"""

보험사별 문서 항목 클래스 입니다

"""

from sqlalchemy import Column, BigInteger, NVARCHAR, Boolean

from api import Base


class InsuranceDocumentItemClass(Base):
    __tablename__ = "ec_insurance_document_item"
    __table_args__ = {"extend_existing": True}

    seq = Column(BigInteger, autoincrement=True, primary_key=True)
    insurance_code = Column(NVARCHAR(length=200), nullable=False, default="")
    name = Column(NVARCHAR(length=200), nullable=False, default="")
    description = Column(NVARCHAR(length=200), nullable=False, default="")
    essential_input_flag = Column(Boolean, nullable=False, default=False)
    active = Column(Boolean, nullable=False, default=True)
    create_date = Column(BigInteger, nullable=False, default=0)
    update_date = Column(BigInteger, nullable=False, default=0)

    def __str__(self):
        print('InsuranceDocumentItemClass toString : {}'.format(self.__dict__))
