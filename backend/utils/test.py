# import ollama

# prompt = """
# You are a local agriculture assistant.
# Based on these details:
# Crop: Rice
# Stage: Flowering
# Fertilizer: Urea (30 kg/acre)
# Irrigation: 25 mm/week
# Predicted yield: 4200 kg/ha

# Write short, simple advice for the farmer in english,keep it professional.
# """

# response = ollama.chat(model="gemma2:2b", messages=[{"role": "user", "content": prompt}])
# print("\n--- Model Output ---\n")
# print(response["message"]["content"])


import requests
KEY = "9c9ea8bc28a2ead2f0c715f04fe5e2f9"
payload = {
    "name": "test",
    "geo_json": {
        "type": "Feature",
        "properties": {},
        "geometry": {
            "type": "Polygon",
            "coordinates": [[[77.57, 13.03],[77.58, 13.03],[77.58, 13.04],[77.57, 13.04],[77.57, 13.03]]]
        }
    }
}
res = requests.post(f"http://api.agromonitoring.com/agro/1.0/polygons?appid={KEY}", json=payload)
print(res.status_code, res.text)
