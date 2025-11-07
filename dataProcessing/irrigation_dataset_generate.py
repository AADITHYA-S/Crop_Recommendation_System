import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
from tqdm import tqdm
import os

# ================================================================
# CONFIGURATION
# ================================================================
OUTPUT_PATH = r"C:\ABHIRAM\Mini Project\crop_system\data\irrigation_dataset.csv"

CROPS = [
    "bajra", "barley", "cotton", "groundnut", "maize", "millets",
    "oilseeds", "pigeonpea", "pulses", "rice", "sorghum", "soybean",
    "sugarcane", "tobacco", "wheat"
]

STAGES = ["germination", "vegetative", "flowering", "grainfill"]

DISTRICTS = [
    {"state":"Punjab", "district":"Ludhiana"},
    {"state":"Haryana", "district":"Hisar"},
    {"state":"Uttar Pradesh", "district":"Kanpur"},
    {"state":"Bihar", "district":"Patna"},
    {"state":"Madhya Pradesh", "district":"Indore"},
    {"state":"Maharashtra", "district":"Nagpur"},
    {"state":"Gujarat", "district":"Surat"},
    {"state":"West Bengal", "district":"Kolkata"},
    {"state":"Odisha", "district":"Cuttack"},
    {"state":"Chhattisgarh", "district":"Raipur"},
    {"state":"Telangana", "district":"Hyderabad"},
    {"state":"Andhra Pradesh", "district":"Vijayawada"},
    {"state":"Karnataka", "district":"Dharwad"},
    {"state":"Tamil Nadu", "district":"Coimbatore"},
    {"state":"Kerala", "district":"Thrissur"},
    {"state":"Assam", "district":"Nagaon"},
    {"state":"Rajasthan", "district":"Jaipur"},
    {"state":"Jammu & Kashmir", "district":"Srinagar"},
    {"state":"Uttarakhand", "district":"Dehradun"},
    {"state":"Maharashtra", "district":"Pune"}
]

SOIL_TYPES = ["Red", "Sandy", "Clayey", "Loamy", "Black", "Silt"]

# Crop durations (days)
CROP_DUR = {
    "rice":120, "wheat":120, "maize":110, "barley":120, "bajra":100,
    "millets":100, "cotton":150, "groundnut":110, "oilseeds":120,
    "pigeonpea":150, "pulses":110, "sorghum":120, "soybean":110,
    "sugarcane":360, "tobacco":150
}

# Stage factors (relative intensity)
STAGE_FACTORS = {
    "germination": (0.6, 0.8),
    "vegetative": (0.9, 1.1),
    "flowering": (1.1, 1.3),
    "grainfill": (0.7, 0.9)
}

# Base crop water requirement (mm/day)
BASE_WATER_REQ = {
    "rice": 6.5,
    "wheat": 3.5,
    "maize": 4.5,
    "millets": 3.0,
    "sorghum": 3.0,
    "cotton": 5.0,
    "groundnut": 4.0,
    "soybean": 3.5,
    "pigeonpea": 3.0,
    "oilseeds": 4.0,
    "barley": 3.0,
    "sugarcane": 7.0,
    "tobacco": 4.5,
    "pulses": 3.0,
    "bajra": 3.0
}

# ================================================================
# HELPER FUNCTIONS
# ================================================================
def season_from_crop(crop):
    kharif = ["rice","maize","millets","cotton","groundnut","soybean","pigeonpea","oilseeds","bajra","sorghum","tobacco"]
    return "Kharif" if crop in kharif else "Rabi"

def random_weather(season):
    if season == "Kharif":
        Tmax = np.random.uniform(30, 38)
        Tmin = Tmax - np.random.uniform(6, 10)
        Hum = np.random.uniform(60, 95)
        Rain = np.random.uniform(0, 5)
    else:
        Tmax = np.random.uniform(20, 30)
        Tmin = Tmax - np.random.uniform(5, 8)
        Hum = np.random.uniform(40, 80)
        Rain = np.random.uniform(0, 10)
    Wind = np.random.uniform(1, 4)
    SR = np.random.uniform(10, 25)
    return Tmax, Tmin, Hum, Rain, Wind, SR

def estimate_et0(Tmax, Tmin, Hum, SR):
    temp_avg = (Tmax + Tmin)/2
    et0 = 0.0023 * (temp_avg + 17.8) * np.sqrt(Tmax - Tmin) * (SR/10)
    et0 = np.clip(et0, 2, 8)
    return round(et0, 2)

def ndvi_by_stage(stage):
    vals = {"germination":np.random.uniform(0.2,0.4),
            "vegetative":np.random.uniform(0.5,0.75),
            "flowering":np.random.uniform(0.6,0.85),
            "grainfill":np.random.uniform(0.4,0.7)}
    return round(vals[stage],3)

# ================================================================
# DATA GENERATION
# ================================================================
records = []
today = datetime.now().date()

for crop in tqdm(CROPS):
    duration = CROP_DUR[crop]
    season = season_from_crop(crop)

    for d in DISTRICTS:
        for stage in STAGES:
            stage_days = 10
            stage_start_day = {"germination":0, "vegetative":duration*0.25,
                               "flowering":duration*0.55, "grainfill":duration*0.8}[stage]
            for i in range(stage_days):
                day = int(stage_start_day + i)
                sowing_date = today - timedelta(days=day)
                date = sowing_date + timedelta(days=day)

                Tmax, Tmin, Hum, Rain, Wind, SR = random_weather(season)
                ET0 = estimate_et0(Tmax, Tmin, Hum, SR)

                soil_type = random.choice(SOIL_TYPES)
                soil_moist = np.random.uniform(25, 80)
                soil_depth = np.random.uniform(30, 150)
                whc = np.random.uniform(30, 60)
                N = np.random.uniform(10, 60)
                P = np.random.uniform(10, 60)
                K = np.random.uniform(10, 60)

                ndvi = ndvi_by_stage(stage)
                surf_temp = (Tmax + Tmin)/2 + (1-ndvi)*2

                # realistic water requirement based on crop × stage
                base_wr = BASE_WATER_REQ[crop]
                factor = np.random.uniform(*STAGE_FACTORS[stage])
                water_req = round(base_wr * factor, 2)

                # adjust irrigation by rainfall and soil moisture
                irrig = max(water_req - (Rain/1.2) - (soil_moist/30), 0)
                irrig = round(irrig, 2)

                records.append({
                    "Date": date,
                    "State": d["state"],
                    "District": d["district"],
                    "Crop": crop,
                    "Crop_Stage": stage,
                    "Season": season,
                    "Days_Since_Sowing": day,
                    "Crop_Duration": duration,
                    "Soil_Type": soil_type,
                    "Soil_Moisture": round(soil_moist, 2),
                    "Soil_Depth": round(soil_depth, 1),
                    "Soil_Water_Holding_Capacity": round(whc, 1),
                    "Soil_N": round(N, 1),
                    "Soil_P": round(P, 1),
                    "Soil_K": round(K, 1),
                    "Rainfall": round(Rain, 2),
                    "Temperature_Max": round(Tmax, 2),
                    "Temperature_Min": round(Tmin, 2),
                    "Humidity": round(Hum, 2),
                    "Wind_Speed": round(Wind, 2),
                    "Solar_Radiation": round(SR, 2),
                    "ET0": ET0,
                    "NDVI": ndvi,
                    "Surface_Temp": round(surf_temp, 2),
                    "Water_Requirement": water_req,
                    "Irrigation_Level": irrig
                })

# ================================================================
# SAVE
# ================================================================
df = pd.DataFrame(records)
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
df.to_csv(OUTPUT_PATH, index=False)

print(f"✅ Realistic irrigation dataset generated successfully!")
print(f"💾 Saved to: {OUTPUT_PATH}")
print(f"Rows: {len(df)}, Columns: {len(df.columns)}")
print(f"Mean irrigation (mm/day): {df['Irrigation_Level'].mean():.2f}")
print(f"Non-zero irrigation %: {(df['Irrigation_Level']>0).mean()*100:.1f}%")
