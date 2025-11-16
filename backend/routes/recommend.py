from fastapi import FastAPI,APIRouter,Depends,HTTPException,Header
import numpy as np
from datetime import date
from schemas.cropInput import cropInput
from utils.weatherAPI import get_weather
from utils.ndviAPI import get_farm_data
from utils.nutrientCalci import calculate_nutrient_needs
from utils.waterRequirnment import get_daily_water_req
from utils.textRec import generate_recommendations
from sqlalchemy.orm import Session
from database.database import get_db
from database.farmer import Farmer
from database.fields import Field
from database.model_input import ModelInput
from database.model_output import ModelOutput
from database.recommendations import Recommendation
from utils.auth import get_current_farmer
from utils.fertilizer_recommender import recommend_fertilizer
from utils.prepare_model_input import prepare_model_input
from utils.prepare_model_output import prepare_model_output
from utils.text_parser import parse_recommendations
import joblib
# from models.model_utils import predict_crop
encoder = joblib.load("models/pkl/encoders.pkl")
modelA=joblib.load("models/pkl/crop_stage_model.pkl")
modelB1=joblib.load("models/pkl/fertilizer_type_model.pkl")
modelB2=joblib.load("models/pkl/fertilizer_quantity_model.pkl")
modelC=joblib.load("models/pkl/irrigation_model.pkl")
modelD=joblib.load("models/pkl/yeild_model.pkl")

router=APIRouter()

@router.post("/recommend")
def recommendations(data:cropInput, db: Session=Depends(get_db),authorization: str = Header(default=None), user=Depends(get_current_farmer)):
    try:   
        farmer = db.query(Farmer).filter(Farmer.user_id == user.id).first()
        if not farmer:
            raise HTTPException(status_code=404,detail="Farmer not found")
        
        field = db.query(Field).filter(Field.farmer_id == farmer.id).first()

        if not field:
            raise HTTPException(status_code=404,detail="Field not found")

        lat,lon, area = field.latitude, field.longitude, field.area
        soil_type=field.soil_type
        lang=farmer.language

        weather=get_weather(lat,lon)

        invalid_polygon = (
        farmer.polygon_id is None or
        str(farmer.polygon_id).strip() == "" or
        str(farmer.polygon_id).strip().upper() == "NULL"
        )
        ndvi=get_farm_data(lat,lon,area,farmer.name, existing_polygon_id=None if invalid_polygon else farmer.polygon_id)
        print("farmer.polygon_id BEFORE:", repr(farmer.polygon_id))

        if farmer.polygon_id or str(farmer.polygon_id).strip()=="":
            farmer.polygon_id = ndvi["polygon_id"]
            db.commit()

        # nutrients=calculate_nutrient_needs(data.crop,data.n,data.p,data.k)
        waterReq=get_daily_water_req(data.crop)
        today=date.today()
        days_since_sowing=(today-data.sowing_date).days
        print("DAYS SINCE SOWING:",days_since_sowing)
    
        crop_encoder = encoder["Crop"]
        crop_name = (data.crop or "").strip().lower()
        encoder_map = {cls.lower(): i for i, cls in enumerate(crop_encoder.classes_)}
        crop_encoded = encoder_map.get(crop_name, -1)

        
        soil_encoder = encoder["Soil_Type"]
        soil_name = (soil_type or "").strip().lower()
        soil_map = {cls.lower(): i for i, cls in enumerate(soil_encoder.classes_)}
        soil_encoded = encoder_map.get(crop_name, -1)

        model_input=prepare_model_input(data,crop_encoded,soil_encoded,days_since_sowing,weather,ndvi,waterReq)
        db_input=ModelInput(
            field_id=field.id,
            input_snap=model_input
        )
        db.add(db_input)
        db.flush() 
        db.refresh(db_input)
        model_input_id=db_input.id

        user_input_stage={"latest_ndvi":ndvi["latest_ndvi"],"humidity":weather["humidity"],"days_since_sowing":days_since_sowing,"crop_encoded":crop_encoded}   
        stage=modelA.predict([[user_input_stage["latest_ndvi"], user_input_stage["humidity"], user_input_stage["days_since_sowing"], user_input_stage["crop_encoded"]]])


        # fertilizer_type=modelB1.predict([[data.crop,data.n,data.p,data.k,nutrients["n_need"],nutrients["p_need"],nutrients["k_need"]]])

        user_input={"Temperature":weather["temp"],"Humidity":weather["humidity"],"Moisture":ndvi["soil"]["moisture"],"Soil_Type":soil_type,"Crop":data.crop,"Nitrogen":data.n,"Phosphorous":data.p,"Potassium":data.k}
        fertilizer=recommend_fertilizer(user_input)

        user_input_irrigation={"crop_encoded":crop_encoded,"moisture":ndvi["soil"]["moisture"],"rainfall":weather["rainfall"],"latest_ndvi":ndvi["latest_ndvi"],"waterReq":waterReq}
        irrigation=modelC.predict([[user_input_irrigation["crop_encoded"], user_input_irrigation["moisture"], user_input_irrigation["rainfall"], user_input_irrigation["latest_ndvi"], user_input_irrigation["waterReq"]]])

        user_input_yield={"temp":weather["temp"],"rainfall":weather["rainfall"],"moisture":ndvi["soil"]["moisture"],"soil_encoded":soil_encoded,"crop_encoded":crop_encoded,"stage":stage[0],"latest_ndvi":ndvi["latest_ndvi"]}
        yield_pred=modelD.predict([[user_input_yield["temp"], user_input_yield["rainfall"], user_input_yield["moisture"], user_input_yield["soil_encoded"], user_input_yield["crop_encoded"], user_input_yield["stage"], user_input_yield["latest_ndvi"]]])


        preds={
            "crop_stage": str(stage[0]),
        # "fertilizer_type": str(fertilizer_type[0]),
        "fertilizer": fertilizer,
        "irrigation": float(irrigation[0]),
        "yield": float(yield_pred[0])
        }

        model_output=prepare_model_output(preds)
        db_output=ModelOutput(
            field_id=field.id,
            model_input_id=model_input_id,
            predicted_yield=model_output["yield"],
            irrigation=model_output["irrigation"],  
            required_n=model_output["required_n"],
            required_p=model_output["required_p"],
            required_k=model_output["required_k"],
            crop_stage=model_output["crop_stage"]   
        )
        db.add(db_output)
        db.flush()
        db.refresh(db_output)
        model_output_id=db_output.id

        output=generate_recommendations(preds,data.crop,lang)
        print("TYPE OF OUTPUT:", type(output), output)

        parsed_output = parse_recommendations(output)
        fert = parsed_output.get("fertilizer", {}) or {}
        irr = parsed_output.get("irrigation", {}) or {}
        weather = parsed_output.get("weather_warning")
        db_recommendation=Recommendation(
            field_id=field.id,
            model_output_id=model_output_id,
            recommendation_text = output
        )
        db.add(db_recommendation)
        db.flush()
        db.refresh(db_recommendation)
        
        
    except Exception as e:
        print("🔥 BACKEND ERROR:", str(e))
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    db.commit()       
    return {"recommendations": output}

