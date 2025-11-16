# fertilizer_recommender.py

import joblib
import numpy as np
import pandas as pd

# -------------------------------
# LOAD MODELS & ENCODERS
# -------------------------------

N_model = joblib.load("models/pkl/N_need_model.pkl")
P_model = joblib.load("models/pkl/P_need_model.pkl")
K_model = joblib.load("models/pkl/K_need_model.pkl")

encoders = joblib.load("models/pkl/encoders.pkl")

# -------------------------------
# FERTILIZER NPK PERCENTAGES
# -------------------------------

FERTILIZER_NPK = {
    "Urea": {"N": 0.46, "P": 0.0, "K": 0.0},
    "DAP": {"N": 0.18, "P": 0.46, "K": 0.0},
    "MOP": {"N": 0.0,  "P": 0.0,  "K": 0.60},
    "17-17-17": {"N": 0.17, "P": 0.17, "K": 0.17},
    "14-35-14": {"N": 0.14, "P": 0.35, "K": 0.14},
    "10-26-26": {"N": 0.10, "P": 0.26, "K": 0.26},
    "Compost": {"N": 0.01, "P": 0.008, "K": 0.008},
}

# -------------------------------
# PREDICT NUTRIENT NEEDS (N,P,K)
# -------------------------------

def predict_nutrient_needs(input_features: dict):
    """
    input_features = {
        "Temperature": ...,
        "Humidity": ...,
        "Moisture": ...,
        "Soil_Type": ...,
        "Crop": ...,
        "Nitrogen": ...,
        "Phosphorous": ...,
        "Potassium": ...
    }
    """
    df = pd.DataFrame([input_features])

    # Encode categorical features
    for col in ["Crop", "Soil_Type"]:
        le = encoders[col]
        df[col] = df[col].apply(lambda v: le.transform([v])[0] if v in le.classes_ else -1)

    # Predict using models
    N_need = float(N_model.predict(df)[0])
    P_need = float(P_model.predict(df)[0])
    K_need = float(K_model.predict(df)[0])

    return {"N_need": max(N_need, 0), 
            "P_need": max(P_need, 0), 
            "K_need": max(K_need, 0)}

# -------------------------------
# RULE-BASED FERTILIZER SELECTION
# -------------------------------

def choose_fertilizer_group(N_need, P_need, K_need):
    
    if P_need > 25:  
        return "Phosphatic"     # DAP, 14-35-14, 10-26-26
    
    if K_need > 20:
        return "Potassic"       # MOP
    
    if N_need > 35:
        return "Nitrogenous"    # Urea
    
    if N_need > 15 and P_need > 10 and K_need > 10:
        return "Balanced"       # 17-17-17
    
    return "Organic"

# -------------------------------
# MAP GROUP → SPECIFIC FERTILIZER
# -------------------------------

def pick_fertilizer_by_group(group):
    mapping = {
        "Phosphatic": "DAP",
        "Potassic": "MOP",
        "Nitrogenous": "Urea",
        "Balanced": "17-17-17",
        "Organic": "Compost",
    }
    return mapping[group]

# -------------------------------
# CALCULATE FERTILIZER QUANTITY
# -------------------------------

def calculate_quantity(fertilizer, N_need, P_need, K_need):
    npk = FERTILIZER_NPK[fertilizer]

    quantities = []

    if npk["N"] > 0:
        quantities.append(N_need / npk["N"])
    if npk["P"] > 0:
        quantities.append(P_need / npk["P"])
    if npk["K"] > 0:
        quantities.append(K_need / npk["K"])

    if not quantities:
        return 0  # Organic case

    return round(max(quantities), 2)  # highest requirement dominates

# -------------------------------
# FINAL RECOMMENDER FUNCTION
# -------------------------------

def recommend_fertilizer(input_features):
    needs = predict_nutrient_needs(input_features)

    N_need = needs["N_need"]
    P_need = needs["P_need"]
    K_need = needs["K_need"]

    group = choose_fertilizer_group(N_need, P_need, K_need)
    fertilizer = pick_fertilizer_by_group(group)
    quantity = calculate_quantity(fertilizer, N_need, P_need, K_need)

    return {
        "fertilizer_group": group,
        "fertilizer_name": fertilizer,
        "quantity_kg_per_acre": quantity,
        "nutrient_needs": needs
    }
