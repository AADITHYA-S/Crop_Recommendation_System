from sqlalchemy import Column, Integer, String, Float, JSON, ForeignKey, DateTime
from sqlalchemy.sql import func
from database.database import Base

class SuitabilityHistory(Base):
    __tablename__ = "suitability"

    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(String, ForeignKey("farmers.id"))
    crop = Column(String)
    score = Column(Float)
    status = Column(String)
    alternatives = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
