from sqlalchemy import JSON, Column, Integer, Float, ForeignKey,String,DateTime,JSON,func,Text
from database.database import Base
from sqlalchemy.orm import relationship

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    field_id = Column(Integer, ForeignKey("fields.id"), nullable=False)
    model_output_id = Column(Integer, ForeignKey("model_output.id"), nullable=False,unique=True)

    recommendation_text = Column(Text, nullable=False)
    recommendation_date= Column(DateTime, server_default=func.now())


    # Relationship back to ModelOutput
    model_output = relationship("ModelOutput", back_populates="recommendations")
    # Relationship back to Field
    field = relationship("Field", back_populates="recommendations")
    