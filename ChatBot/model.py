import uuid
from sqlalchemy import Column, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ChtBt(Base):
    __tablename__ = 'cht_bt'
    __table_args__ = {'schema': 'public'} 

    mes_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    msg_user = Column(Text, nullable=True)
    req_sql = Column(Text, nullable=True)
    res_user = Column(Text, nullable=True)
    ct_msg = Column(Text, nullable=True)
    user_id = Column(Text, nullable=True)
    dt_res_user = Column(TIMESTAMP, nullable=True)
    dt_msg = Column(TIMESTAMP, nullable=True)
    conv_id = Column(Text, nullable=True)