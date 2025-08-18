from sqlalchemy import create_engine, Column, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import hashlib
import json
from datetime import datetime, timedelta

Base = declarative_base()

class ScrapedData(Base):
    __tablename__ = 'scraped_data'
    id = Column(String(64), primary_key=True)
    url = Column(String(2048))
    data = Column(Text)
    timestamp = Column(DateTime)
    
    def __init__(self, url, data):
        self.id = hashlib.sha256(url.encode()).hexdigest()
        self.url = url
        self.data = json.dumps(data)
        self.timestamp = datetime.utcnow()

def init_db():
    engine = create_engine('sqlite:///scraped_data.db')
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)

def save_data(url, data):
    Session = init_db()
    session = Session()
    
    # Check if data exists and is recent (within 24 hours)
    data_id = hashlib.sha256(url.encode()).hexdigest()
    existing = session.query(ScrapedData).filter_by(id=data_id).first()
    
    if existing and (datetime.utcnow() - existing.timestamp) < timedelta(hours=24):
        # Update existing record
        existing.data = json.dumps(data)
        existing.timestamp = datetime.utcnow()
    else:
        # Create new record
        new_entry = ScrapedData(url, data)
        session.merge(new_entry)
    
    session.commit()
    session.close()
    return data_id

def get_data(api_key):
    Session = init_db()
    session = Session()
    result = session.query(ScrapedData).filter_by(id=api_key).first()
    session.close()
    
    if result:
        # Check if data is stale (older than 24 hours)
        if (datetime.utcnow() - result.timestamp) > timedelta(hours=24):
            return None
        return json.loads(result.data)
    return None
