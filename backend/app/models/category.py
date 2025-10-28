"""
SQLAlchemy модель Category
"""
from sqlalchemy import Column, Integer, String, Text, ARRAY, TIMESTAMP
from sqlalchemy.sql import func
from app.database import Base

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    keywords = Column(ARRAY(String), default=[])
    avg_visit_duration = Column(Integer, default=30, nullable=False)
    icon = Column(String(50))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
