import pandas as pd
import numpy as np
import random
import os

# ----------------------------------
# CONFIG
crops = ['bajra', 'barley', 'cotton', 'groundnut', 'maize', 'millets', 'oilseeds',
         'pigeonpea', 'pulses', 'rice', 'sorghum', 'soybean', 'sugarcane', 'tobacco', 'wheat']

soils = ['Red', 'Sandy', 'Clayey', 'Silt', 'Loamy', 'Black']

# Fertilizers grouped by type
chemical_ferts = ['Urea', 'DAP', '14-35-14', '28-28', '17-17-17', '20-20', '10-26-26', 'MOP']
organic_ferts = ['Compost', 'Vermicompost', 'Green Manure', 'Organic Manure']

# Combine into single mapping
fertilizer_type_map = {f: "Chemical" for f in chemical_ferts}
fertilizer_type_map.update({f: "Organic" for f in organic_ferts})

all_fertilizers = chemical_ferts + organic_ferts

# ----------------------------------
# Generate one record
def generate_sample(crop, soil):
    # realistic random environmental conditions
    temp = np.clip(np.random.normal(30, 4), 20, 40)
    hum = np.clip(np.random.normal(65, 10), 40, 90)
    moist = np.clip(np.random.normal(30, 10), 10, 50)
    N = np.clip(np.random.normal(80, 30), 0, 140)
    P = np.clip(np.random.normal(40, 20), 5, 120)
    K = np.clip(np.random.normal(60, 30), 5, 200)

    # adjust by soil
    if soil in ['Sandy', 'Red']:
        N -= random.uniform(5, 15)
        moist -= random.uniform(5, 10)
    elif soil in ['Clayey', 'Loamy']:
        moist += random.uniform(5, 10)

    # adjust by crop
    if crop in ['rice', 'sugarcane']:
        moist += random.uniform(5, 10)
        N += random.uniform(10, 20)
    elif crop in ['groundnut', 'pulses', 'soybean']:
        N -= random.uniform(10, 20)
    elif crop in ['wheat', 'barley']:
        P += random.uniform(10, 15)

    # fertilizer logic (simple rule-based)
    if N < 30:
        fert = "Urea"
    elif P < 25:
        fert = "DAP"
    elif K < 30:
        fert = "MOP"
    elif crop in ['rice', 'sugarcane', 'maize']:
        fert = random.choice(["17-17-17", "20-20", "10-26-26", "28-28"])
    elif crop in ['groundnut', 'pulses', 'soybean', 'pigeonpea']:
        fert = random.choice(organic_ferts)
    else:
        fert = random.choice(all_fertilizers)

    fert_type = fertilizer_type_map.get(fert, "Unknown")

    return [round(temp, 2), round(hum, 2), round(moist, 2),
            soil, crop, int(N), int(P), int(K), fert, fert_type]

# ----------------------------------
# Generate full dataset
rows = []
for crop in crops:
    for soil in soils:
        for _ in range(100):  # 100 samples per crop-soil pair
            rows.append(generate_sample(crop, soil))

columns = ["Temperature", "Humidity", "Moisture", "Soil Type", "Crop Type",
           "Nitrogen", "Phosphorous", "Potassium", "Fertilizer Name", "Fertilizer Type"]

df = pd.DataFrame(rows, columns=columns)

# ----------------------------------
# Save to CSV
# os.makedirs("datasets", exist_ok=True)
csv_path = os.path.join("data", "fertilizer_dataset_full.csv")
df.to_csv(csv_path, index=False)

print(f"✅ Synthetic realistic fertilizer dataset generated!")
print(f"📁 Saved to: {os.path.abspath(csv_path)}")
print(f"Total records: {len(df)} ({len(crops)} crops × {len(soils)} soils × 100 samples)")

