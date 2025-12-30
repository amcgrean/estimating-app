from project import create_app, db
import sqlite3  # Replace this with the appropriate DB connector for your setup, e.g., psycopg2 for PostgreSQL

from sqlalchemy import create_engine, Column, Integer, String, Text, Date, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Define your SQLite database connection
DATABASE_URI = 'sqlite:////home/amcgrean/mysite/instance/bids.db'

# Initialize SQLAlchemy
engine = create_engine(DATABASE_URI)
Base = declarative_base()

# Define the it_service table schema
class ITService(Base):
    __tablename__ = 'it_service'

    ID = Column(Integer, primary_key=True, autoincrement=True)
    issue_type = Column(String(255), nullable=False)
    createdby = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(50), default='Open')
    updatedby = Column(String(255), nullable=True)
    updatedDate = Column(Date, default=datetime.utcnow)
    notes = Column(Text, nullable=True)

# Create the table in the database
Base.metadata.create_all(engine)

print("Table it_service created successfully!")
