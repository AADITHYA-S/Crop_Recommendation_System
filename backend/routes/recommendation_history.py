from fastapi import FastAPI,APIRouter,Depends, Header
from sqlalchemy.orm import Session  
from database.model_output import ModelOutput
from database.fields import Field
from database.farmer import Farmer
from database.database import get_db
from database.recommendations import Recommendation


router=APIRouter()

@router.get("/user/last-recommendation")
def get_last_recommendation(
    user_id: str = Header(alias="user-id"),   # IMPORTANT FIX
    db: Session = Depends(get_db)
):
    farmer = db.query(Farmer).filter(Farmer.user_id == user_id).first()
    if not farmer:
        return {"text": "No farmer found for user."}

    field = db.query(Field).filter(Field.farmer_id == farmer.id).first()
    if not field:
        return {"text": "No field found for user."}

    rec = (
        db.query(Recommendation)
        .filter(Recommendation.field_id == field.id)
        .order_by(Recommendation.recommendation_date.desc())
        .first()
    )

    if not rec:
        return {"text": "No recommendation found."}

    return {"text": rec.recommendation_text}


