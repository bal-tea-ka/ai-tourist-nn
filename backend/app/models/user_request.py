"""
SQLAlchemy модель UserRequest
"""
from sqlalchemy import Column, Integer, String, Text, DECIMAL, ARRAY, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB, INET
from sqlalchemy.sql import func
from app.database import Base

class UserRequest(Base):
    __tablename__ = "user_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_interests = Column(Text, nullable=False)
    available_time_minutes = Column(Integer, nullable=False)
    user_address = Column(Text)
    user_latitude = Column(DECIMAL(10, 8))
    user_longitude = Column(DECIMAL(11, 8))
    selected_places_ids = Column(ARRAY(Integer), default=[])
    selected_category_ids = Column(ARRAY(Integer), default=[])
    route_order = Column(ARRAY(Integer), default=[])
    total_route_time = Column(Integer)
    total_route_distance = Column(DECIMAL(10, 2))
    perplexity_response_1 = Column(JSONB)
    perplexity_response_2 = Column(JSONB)
    execution_time_ms = Column(Integer)
    error_message = Column(Text)
    ip_address = Column(INET)
    user_agent = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())
