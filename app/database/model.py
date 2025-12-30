from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)  # 대화 이름
    date = Column(String, nullable=False)
    messages = Column(Text, nullable=False)
