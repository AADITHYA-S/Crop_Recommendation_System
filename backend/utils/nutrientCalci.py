# utils/nutrient_calculator.py

IDEAL_NPK = {
    "bajra":     {"N": 50,  "P": 25,  "K": 0},    # pearl millet / bajra recommended dose. :contentReference[oaicite:0]{index=0}
    "barley":    {"N": 60,  "P": 30,  "K": 20},   # common irrigated recommendation. :contentReference[oaicite:1]{index=1}
    "cotton":    {"N": 80,  "P": 40,  "K": 40},   # typical state recommendations (hybrid/rainfed variants exist). :contentReference[oaicite:2]{index=2}
    "groundnut": {"N": 25,  "P": 50,  "K": 25},   # groundnut recommendations (P often emphasized). :contentReference[oaicite:3]{index=3}
    "maize":     {"N": 60,  "P": 30,  "K": 30},   # blanket recommendation (alfisols); higher rates used for hybrids. :contentReference[oaicite:4]{index=4}
    "millets":   {"N": 80,  "P": 40,  "K": 40},   # millets/hybrid millet package of practices. :contentReference[oaicite:5]{index=5}
    "oilseeds":  {"N": 25,  "P": 50,  "K": 25},   # typical oilseeds GRD / ICM recommendations (use crop-specific where possible). :contentReference[oaicite:6]{index=6}
    "pigeonpea": {"N": 25,  "P": 40,  "K": 30},   # pigeonpea / pigeon peas: state/ICRISAT guidance. :contentReference[oaicite:7]{index=7}
    "pulses":    {"N": 15,  "P": 50,  "K": 18},   # generic pulses ready-reckoner (15–20 N; 50–60 P2O5; K if deficient). :contentReference[oaicite:8]{index=8}
    "rice":      {"N":100,  "P": 50,  "K": 50},   # (common HYV/hybrid rice recommendations vary — e.g., 100:60:60 for some hybrids). :contentReference[oaicite:9]{index=9}
    "sorghum":   {"N": 90,  "P": 45,  "K": 45},   # sorghum / jowar recommendations. :contentReference[oaicite:10]{index=10}
    "soybean":   {"N": 20,  "P": 40,  "K": 20},   # blanket soybean GRD (watch for S requirement also). :contentReference[oaicite:11]{index=11}
    "sugarcane": {"N":275,  "P": 62.5,"K":112.5}, # state/extension recommended NPK for sugarcane (high N & K). :contentReference[oaicite:12]{index=12}
    "tobacco":   {"N":120,  "P": 60,  "K": 40},   # tobacco has high nutrient demand; check local extension for variety-specific rates. :contentReference[oaicite:13]{index=13}
    "wheat":     {"N":120,  "P": 60,  "K": 40}    # standard wheat recommendation (irrigated timely-sown common value). :contentReference[oaicite:14]{index=14}
}
def calculate_nutrient_needs(crop_name: str, N: float, P: float, K: float):
    ideal = IDEAL_NPK.get(crop_name.lower())
    if not ideal:
        raise ValueError(f"Unknown crop: {crop_name}")

    n_need = max(0, ideal["N"] - N)
    p_need = max(0, ideal["P"] - P)
    k_need = max(0, ideal["K"] - K)

    return {"n_need": n_need, "p_need": p_need, "k_need": k_need}
