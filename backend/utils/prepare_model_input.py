# from schemas.cropInput import cropInput
def prepare_model_input(data, crop_encoded, soil_encoded, days_since_sowing, weather, ndvi, waterReq):

    input_snapshot = {
        "days_since_sowing": days_since_sowing,
        "crop_encoded": crop_encoded,
        "soil_encoded": soil_encoded,
        "temperature": weather["temp"],
        "humidity": weather["humidity"],
        "rainfall": weather["rainfall"],
        "latest_ndvi": ndvi["latest_ndvi"],
        "soil_moisture": ndvi["soil"]["moisture"],
        "water_requirement": waterReq,
        "Soil_N":data.n,
        "Soil_P":data.p,
        "Soil_K":data.k
    }

    # model_input = list(input_snapshot.values())

    return input_snapshot
