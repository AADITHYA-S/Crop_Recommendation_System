import json
import math

with open("C:\ABHIRAM\Mini Project\crop_system\data\crop_req.json") as f:
    CROP_DATA = json.load(f)


def score_range(value, min_val, max_val):
    """
    Returns score (0-1) based on how close value is to the ideal range.
    """
    if min_val <= value <= max_val:
        return 1
    diff = min(abs(value - min_val), abs(value - max_val))
    return max(0, 1 - (diff / (max_val - min_val)))


def calculate_suitability(crop, soil_type, ph, temp, rainfall):
    data = CROP_DATA[crop.lower()]

    soil_score = 1 if soil_type.lower() in data["soil_types"] else 0.5
    ph_score = score_range(ph, data["ph_min"], data["ph_max"])
    temp_score = score_range(temp, data["temp_min"], data["temp_max"])
    rainfall_score = score_range(rainfall, data["rainfall_min"], data["rainfall_max"])

    # Weighted model
    total_score = round(0.25 * soil_score +
                        0.25 * ph_score +
                        0.25 * temp_score +
                        0.25 * rainfall_score, 2)

    label = "Suitable"
    if total_score < 0.4:
        label = "Not Suitable"
    elif total_score < 0.7:
        label = "Moderately Suitable"

    return {
        "crop": crop,
        "score": total_score,
        "label": label,

    }


def suggest_alternatives(soil_type, ph, temp, rainfall, avoid_crop=None):
    results = []

    for crop in CROP_DATA.keys():
        if crop == avoid_crop:
            continue

        suitability = calculate_suitability(
            crop, soil_type, ph, temp, rainfall
        )

        results.append(suitability)

    # Sort by best score
    results = sorted(results, key=lambda x: x["score"], reverse=True)

    return results[:3]  # top 3 alternatives
