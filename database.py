from sqlalchemy import create_engine, Column, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import hashlib
import json
from datetime import datetime, timedelta
import sqlite3

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
    
    # Check if the database exists and needs migration
    migrate_database(engine)
    
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)

def migrate_database(engine):
    """Handle database schema migrations"""
    try:
        # Check if timestamp column exists
        with engine.connect() as conn:
            result = conn.execute("PRAGMA table_info(scraped_data)")
            columns = [row[1] for row in result]
            
            if 'timestamp' not in columns:
                # Migrate to new schema
                conn.execute("ALTER TABLE scraped_data ADD COLUMN timestamp DATETIME")
                conn.execute("UPDATE scraped_data SET timestamp = datetime('now')")
                
    except Exception as e:
        # Table doesn't exist yet, will be created automatically
        pass

def save_data(url, data):
    Session = init_db()
    session = Session()
    
    # Check if data exists and is recent
    data_id = hashlib.sha256(url.encode()).hexdigest()
    existing = session.query(ScrapedData).filter_by(id=data_id).first()
    
    if existing:
        # Update existing record
        existing.data = json.dumps(data)
        existing.timestamp = datetime.utcnow()
    else:
        # Create new record
        new_entry = ScrapedData(url, data)
        session.add(new_entry)
    
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
