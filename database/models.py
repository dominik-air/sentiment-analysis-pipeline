from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, CheckConstraint

Base = declarative_base()

class Users(Base):
    __tablename__ = 'users'
    __table_args__ = (CheckConstraint('length(name) > 0'),)
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable = False)
    
class Tweets(Base):
    __tablename__ = 'tweets'
    __table_args__ = (
        CheckConstraint('length(body) > 0'),
    )
    id = Column(Integer, primary_key=True)
    body = Column(String(300))
    user_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime)

    def __repr__(self):
        return "<tweets(id='{0}', text={1}, user_id={2}, created_date={3})>".format(
            self.id, self.body, self.user_id, self.created_at)
    
class Keywords(Base):
    __tablename__ = 'keywords'
    __table_args__ = (
        CheckConstraint('length(keyword) > 0'),
    )
    id = Column(Integer, primary_key=True)
    tweet_id = Column(Integer, ForeignKey('tweets.id'))
    keyword = Column(String(50))
    
class Sentiments(Base):
    __tablename__ = 'sentiments'
    __table_args__ = (
        CheckConstraint('positive >= 0'),
        CheckConstraint('negative >= 0'),
        CheckConstraint('neutral >= 0')
    )
    id = Column(Integer, primary_key=True)
    tweet_id = Column(Integer, ForeignKey('tweets.id'))
    positive = Column(Float, nullable = False)
    negative = Column(Float, nullable = False)
    neutral = Column(Float, nullable = False)