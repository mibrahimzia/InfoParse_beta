from sqlalchemy import create_engine, Column, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import hashlib
import json

Base = declarative_base()

class ScrapedData(Base):
    __tablename__ = 'scraped_data'
    id = Column(String(64), primary_key=True)
    url = Column(String(2048))
    data = Column(Text)
    
    def __init__(self, url, data):
        self.id = hashlib.sha256(url.encode()).hexdigest()
        self.url = url
        self.data = json.dumps(data)

def init_db():
    engine = create_engine('sqlite:///scraped_data.db')
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)

def save_data(url, data):
    Session = init_db()
    session = Session()
    new_entry = ScrapedData(url, data)
    session.merge(new_entry)
    session.commit()
    session.close()
    return new_entry.id

def get_data(api_key):
    Session = init_db()
    session = Session()
    result = session.query(ScrapedData).filter_by(id=api_key).first()
    session.close()
    return json.loads(result.data) if result else None