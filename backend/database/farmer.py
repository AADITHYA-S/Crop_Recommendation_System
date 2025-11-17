from sqlalchemy import Column,Integer,Float,String
from database.database import Base
from sqlalchemy.orm import relationship

class Farmer(Base):
    __tablename__ = "farmers"

    id = Column(Integer, primary_key=True, index=True)
    user_id=Column(String,unique=True,index=True)
    name = Column(String)
    phone = Column(String, nullable=True)
    # email = Column(String, unique=True, index=True)
    language = Column(String)
    polygon_id = Column(String, nullable=True)

    # Relationship to Field
    fields = relationship("Field", back_populates="farmer")
