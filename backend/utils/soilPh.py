import requests

def get_soil_ph(lat, lon):
    url = (
        "https://rest.isric.org/soilgrids/v2.0/properties/query"
        f"?lon={lon}&lat={lat}&property=phh2o"
    )

    res = requests.get(url)

    if res.status_code != 200:
        print("SoilGrids error:", res.text)
        return None

    data = res.json()

    try:
        layers = data["properties"].get("layers", [])
        if not layers:
            print("No layers found")
            return None

        # find the phh2o layer
        ph_layer = next((layer for layer in layers if layer.get("name") == "phh2o"), None)
        if not ph_layer:
            print("phh2o layer missing")
            return None

        depths = ph_layer.get("depths", [])
        if not depths:
            print("No depths in ph layer")
            return None

        # Try to use 0-5 cm (topsoil)
        topsoil = depths[0]  # 0-5 cm range
        values = topsoil.get("values", {})

        # SoilGrids returns Q0.5 (median) as the main value
        ph_val = values.get("Q0.5") or values.get("mean")

        if ph_val is None:
            print("Topsoil pH is None")
            return None

        # SoilGrids returns pH*10 (if d_factor = 10)
        d_factor = ph_layer["unit_measure"].get("d_factor", 1)
        return round(ph_val / d_factor, 2)

    except Exception as e:
        print("Soil pH parsing error:", e)
        return None
