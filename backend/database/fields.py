from sqlalchemy import Column, Integer, Float, ForeignKey,String
from database.database import Base
from sqlalchemy.orm import relationship

class Field(Base):
    __tablename__ = "fields"

    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id"),nullable=False)
    latitude = Column(Float)
    longitude = Column(Float)
    area = Column(Float)
    soil_type=Column(String)


    # Relationship back to Farmer
    farmer = relationship("Farmer", back_populates="fields")
    # Relationship to ModelInput
    inputs = relationship("ModelInput", back_populates="field")
    # Relationship to ModelOutput
    model_output = relationship("ModelOutput", back_populates="field")
    # Relationship to Reccomendation
    recommendations = relationship("Recommendation", back_populates="field")
