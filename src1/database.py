'''DATABASE CONNECTION '''
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine,Column,String
from sqlalchemy.orm import sessionmaker
Base = declarative_base()

class TweetDetails(Base):
    '''SQLALCHEMY ORM MODEL'''
    __tablename__='Tweeted_data'
    id = Column(String(200), primary_key=True)
    text = Column(String(200))
    edit_history_tweet_ids = Column(String(300))


DATABASE_URL = 'mysql+pymysql://root:root@localhost:3306/Twitter_Api'

#  MySQL database engine
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)

# Create a session
Session = sessionmaker(bind=engine)
