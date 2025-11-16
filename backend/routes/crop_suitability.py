from fastapi import APIRouter, HTTPException, Depends, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel
# from sqlalchemy.orm import Session
from utils.auth import get_current_farmer
from database.database import get_db
from utils.weatherAPI import get_weather
# from utils. import get_soil_data
from utils.ndviAPI import get_farm_data
from utils.suitability import calculate_suitability, suggest_alternatives
from database.farmer import Farmer
from database.fields import Field
from utils.soilPh import get_soil_ph
from database.suitability import SuitabilityHistory


router = APIRouter()

class SuitabilityInput(BaseModel):
    crop: str


@router.post("/suitability")
async def suitability(data: SuitabilityInput,db: Session=Depends(get_db),authorization: str = Header(default=None), user=Depends(get_current_farmer)):

    farmer = db.query(Farmer).filter(Farmer.user_id == user.id).first()
    if not farmer:
        raise HTTPException(status_code=404,detail="Farmer not found")
    
    field = db.query(Field).filter(Field.farmer_id == farmer.id).first()

    if not field:
        raise HTTPException(status_code=404,detail="Field not found")

    lat,lon, area = field.latitude, field.longitude, field.area
    # Fetch weather data
    weather =get_weather(lat,lon)
    if not weather:
        raise HTTPException(500, "Weather data unavailable")

    # Fetch soil data
    soil=field.soil_type
    ph= get_soil_ph(lat,lon)
    if ph is None:
        ph=6.5  # default pH

    


    # Fetch NDVI
    invalid_polygon = (
        farmer.polygon_id is None or
        str(farmer.polygon_id).strip() == "" or
        str(farmer.polygon_id).strip().upper() == "NULL"
        )
    ndvi_data =get_farm_data(lat,lon,area,farmer.name, existing_polygon_id=None if invalid_polygon else farmer.polygon_id)

    temperature = weather["temp"]
    rainfall = weather["rainfall"]
    soil_type = soil
    soil_moisture = ndvi_data["soil"]["moisture"]
    ndvi = ndvi_data["latest_ndvi"]

    # Suitability calculation
    result = calculate_suitability(
        crop=data.crop.lower(),
        soil_type=soil_type,
        ph=ph,
        temp=temperature,
        rainfall=rainfall
    )

    # Alternative crops if unsuitable
    alternatives = suggest_alternatives(
    soil_type=soil_type,
    ph=ph,
    temp=temperature,
    rainfall=rainfall,
    avoid_crop=data.crop.lower()
    )

    history = SuitabilityHistory(
    farmer_id=farmer.id,
    crop=data.crop.lower(),
    score=result["score"],
    status=result["label"],
    alternatives=alternatives  # JSON stored directly
)

    db.add(history)
    db.commit()
    db.refresh(history)

    return {
        "suitability": result,
        "alternatives": alternatives
    }
