import pandas as pd

# Load your dataset
df = pd.read_csv(r"C:\ABHIRAM\Mini Project\crop_system\data\fertilizer_dataset_full.csv")

# ------------------------------------------------------------------
# 1️⃣ Optimal NPK values for all 15 crops (kg/ha)
optimal_npk = {
    "Rice": {"N": 100, "P": 60, "K": 60},
    "Wheat": {"N": 100, "P": 50, "K": 40},
    "Maize": {"N": 200, "P": 75, "K": 75},
    "Barley": {"N": 60, "P": 30, "K": 20},
    "Bajra": {"N": 50, "P": 25, "K": 25},
    "Millets": {"N": 70, "P": 35, "K": 35},
    "Sorghum": {"N": 80, "P": 40, "K": 40},
    "Cotton": {"N": 90, "P": 50, "K": 70},
    "Groundnut": {"N": 30, "P": 50, "K": 60},
    "Pulses": {"N": 25, "P": 30, "K": 30},
    "Pigeonpea": {"N": 25, "P": 45, "K": 30},
    "Soybean": {"N": 20, "P": 40, "K": 30},
    "Oilseeds": {"N": 60, "P": 40, "K": 30},
    "Sugarcane": {"N": 300, "P": 100, "K": 200},
    "Tobacco": {"N": 100, "P": 50, "K": 100}
}

# ------------------------------------------------------------------
# 2️⃣ Fertilizer nutrient compositions (percentage nutrient content)
fertilizer_content = {
    # Chemical fertilizers
    "Urea": {"N": 46, "P": 0, "K": 0},
    "DAP": {"N": 18, "P": 46, "K": 0},
    "MOP": {"N": 0, "P": 0, "K": 60},
    "14-35-14": {"N": 14, "P": 35, "K": 14},
    "28-28": {"N": 28, "P": 28, "K": 0},
    "17-17-17": {"N": 17, "P": 17, "K": 17},
    "20-20": {"N": 20, "P": 20, "K": 0},
    "10-26-26": {"N": 10, "P": 26, "K": 26},
    # Organic fertilizers (approximate nutrient contents)
    "Compost": {"N": 1.5, "P": 1, "K": 1.5},
    "Vermicompost": {"N": 2, "P": 1.5, "K": 1.5},
    "Green Manure": {"N": 0.5, "P": 0.2, "K": 0.5},
    "Organic Manure": {"N": 1.5, "P": 0.5, "K": 1.0}
}

# ------------------------------------------------------------------
# 3️⃣ Compute deficiency per crop (need_N, need_P, need_K)
def compute_deficiency(row):
    crop = row["Crop Type"].strip().capitalize()
    if crop not in optimal_npk:
        # if unknown, leave same values (no correction)
        return row["Nitrogen"], row["Phosphorous"], row["Potassium"]
    opt = optimal_npk[crop]
    N_need = max(opt["N"] - row["Nitrogen"], 0)
    P_need = max(opt["P"] - row["Phosphorous"], 0)
    K_need = max(opt["K"] - row["Potassium"], 0)
    return N_need, P_need, K_need

df[["N_need", "P_need", "K_need"]] = df.apply(lambda r: pd.Series(compute_deficiency(r)), axis=1)

# ------------------------------------------------------------------
# 4️⃣ Compute fertilizer quantity required to meet those needs
def calculate_fert_amount(row):
    fert = row["Fertilizer Name"]
    if fert not in fertilizer_content:
        return None
    comp = fertilizer_content[fert]

    total = 0
    count = 0

    # Nutrient-based requirement conversion
    if comp["N"] > 0:
        total += (row["N_need"] / comp["N"]) * 100
        count += 1
    if comp["P"] > 0:
        total += (row["P_need"] / comp["P"]) * 100
        count += 1
    if comp["K"] > 0:
        total += (row["K_need"] / comp["K"]) * 100
        count += 1

    return round(total / count, 2) if count > 0 else None

df["Fertilizer Quantity (kg/ha)"] = df.apply(calculate_fert_amount, axis=1)
df["Fertilizer Quantity (kg/acre)"] = (df["Fertilizer Quantity (kg/ha)"] / 2.47).round(2)

# ------------------------------------------------------------------
# 5️⃣ Optional: clip unrealistic high values
df["Fertilizer Quantity (kg/ha)"] = df["Fertilizer Quantity (kg/ha)"].clip(0, 600)

# ------------------------------------------------------------------
# 6️⃣ Save updated file
output_path = r"C:\ABHIRAM\Mini Project\crop_system\data\fertilizer_dataset_full.csv"
df.to_csv(output_path, index=False)

print("✅ Fertilizer quantities for all 15 crops & fertilizers calculated successfully!")
print(f"💾 Saved to: {output_path}")
