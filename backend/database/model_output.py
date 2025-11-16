from sqlalchemy import Column, Integer, Float, ForeignKey,String,DATETIME,JSON,func
from database.database import Base
from sqlalchemy.orm import relationship

class ModelOutput(Base):
    __tablename__ = "model_output"

    id = Column(Integer, primary_key=True, index=True)
    field_id = Column(Integer, ForeignKey("fields.id"), nullable=False)
    model_input_id = Column(Integer, ForeignKey("inputs.id"), nullable=False,unique=True)
    crop_stage=Column(String)
    predicted_yield = Column(Float)
    required_n=Column(Float)
    required_p=Column(Float)
    required_k=Column(Float)
    irrigation=Column(Float)
    created_at=Column(DATETIME, server_default=func.now())

    # Relationship back to ModelInput
    model_input = relationship("ModelInput", back_populates="model_output")
    # Relationship back to Field
    field = relationship("Field", back_populates="model_output")
    # Relationship to Recommendation
    recommendations = relationship("Recommendation", back_populates="model_output",uselist=False)