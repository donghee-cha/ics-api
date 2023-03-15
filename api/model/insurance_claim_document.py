"""

보험사 문서양식 정보 클래스

"""
from sqlalchemy import Column, BigInteger, Integer, TEXT, NVARCHAR

from api import Base


class InsuranceClaimDocumentClass(Base):
    __tablename__ = "ec_insurance_claim_document"
    __table_args__ = {"extend_existing": True}

    seq = Column(BigInteger, autoincrement=True, primary_key=True)
    ec_insurance_code = Column(NVARCHAR(length=200), nullable=False, default="")
    publish_date = Column(BigInteger, nullable=False, default=0)
    document_url = Column(NVARCHAR(length=500), nullable=False, default="")
    size = Column(NVARCHAR(length=200), nullable=False, default="")
    page_count = Column(Integer, nullable=False, default=1)
    coordinate_information = Column(TEXT, nullable=False, default="")
    create_date = Column(BigInteger, nullable=False, default=0)
    update_date = Column(BigInteger, nullable=False, default=0)

    def __str__(self):
        print('InsuranceClaimDocumentClass toString : {}'.format(self.__dict__))
