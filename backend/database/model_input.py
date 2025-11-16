from sqlalchemy import Column, Integer, Float, ForeignKey,String,JSON,DATETIME,func
from database.database import Base
from sqlalchemy.orm import relationship

class ModelInput(Base):
    __tablename__ = "inputs"

    id = Column(Integer, primary_key=True, index=True)
    field_id = Column(Integer, ForeignKey("fields.id"), nullable=False)
    input_snap = Column(JSON)  # Storing as JSON string for simplicity
    created_at = Column(DATETIME, server_default=func.now())

    # Relationship back to Field
    field = relationship("Field", back_populates="inputs")
    # Relationship to ModelOutput
    model_output = relationship("ModelOutput", back_populates="model_input",uselist=False)
