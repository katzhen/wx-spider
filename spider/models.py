# 导入模块
from sqlalchemy import Column, Integer, String, DateTime, Text
from spider import db


class Articles(db.Model):
    __tablename__ = 'articles'
    id = Column(String(36), primary_key=True)
    original_id = Column(Integer)
    title = Column(String(200))
    content = Column(Text)
    cover = Column(String(100))
    url = Column(String(100))
    publish_time = Column(DateTime)
    create_time = Column(DateTime)
