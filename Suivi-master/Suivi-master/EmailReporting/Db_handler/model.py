from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

Base = declarative_base()

class UserRole(Base):
    __tablename__ = 'user_role'
    user_role = Column(String(50), primary_key=True)
    priority = Column(Integer)



class UserInwi(Base):
    __tablename__ = 'user_inwi'
    user_id = Column(Text, primary_key=True)
    name_user = Column(String(50))
    last_name_user = Column(String(50))
    email_user = Column(Text, nullable=False)
    user_role = Column(String(50), ForeignKey("user_role.user_role"), nullable=False)
    password = Column(Text)
    
    role = relationship("UserRole", backref="users")



      
class EmailLo(Base):
    __tablename__ = 'email_lo'
    id = Column(Text, primary_key=True)
    email_rec = Column(Text, nullable=False)
    date_rec = Column(DateTime, nullable=False)
    subject = Column(Text)
    body = Column(Text)
    query_gen = Column(Text)
    body_env = Column(Text)
    date_env = Column(DateTime)
    status = Column(String(255))
    cate_msg = Column(String(255))
    priority = Column(Integer)
    conversation_id = Column(Text)
class LoginHistory(Base):
    __tablename__ = 'login_history'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Text)
    ip_adress = Column(Text)
    success = Column(Text)
    user_agent = Column(Text)
    date_l = Column(DateTime)