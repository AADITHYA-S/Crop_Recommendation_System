import re

def parse_recommendations(raw_text: str):

    # Remove markdown (**bold**)
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", raw_text)

    # Split by bullet points
    bullets = re.split(r"\n\s*\*\s*", text)
    bullets = [b.strip() for b in bullets if b.strip()]

    result = {
        "fertilizer": None,
        "irrigation": None,
        "weather_warning": None,
        "general_advice": []
    }

    def extract_number(pattern, line):
        match = re.search(pattern, line.lower())
        return float(match.group(1)) if match else None

    fert_keywords = ["compost", "urea", "dap", "npk", "mop", "fertilizer"]
    irrigation_keywords = ["water", "irrigate", "mm"]
    weather_keywords = ["weather", "forecast", "rain"]

    def is_fertilizer(line):
        return any(k in line.lower() for k in fert_keywords)

    def is_weather(line):
        return any(k in line.lower() for k in weather_keywords)

    def is_irrigation(line):
        return any(k in line.lower() for k in irrigation_keywords)

    # Skip the intro line (bullets[0])
    for bullet in bullets[1:]:
        lower = bullet.lower()

        # 1️⃣ Fertilizer
        if is_fertilizer(bullet):
            qty = extract_number(r"([0-9]+(?:\.[0-9]+)?)\s*kg", bullet)
            name = next((k.capitalize() for k in fert_keywords if k in lower), None)
            result["fertilizer"] = {
                "name": name,
                "quantity_kg": qty,
                "text": bullet
            }
            continue

        # 2️⃣ Weather (check before irrigation)
        if is_weather(bullet):
            result["weather_warning"] = bullet
            continue

        # 3️⃣ Irrigation
        if is_irrigation(bullet):
            mm = extract_number(r"([0-9]+(?:\.[0-9]+)?)\s*mm", bullet)
            result["irrigation"] = {
                "mm_per_day": mm,
                "text": bullet
            }
            continue

        # 4️⃣ General advice
        result["general_advice"].append(bullet)

    return result



# Example usage:
# raw_text = """Here's some advice for your cotton crop:

# * **Get that compost in!**  Mix 1963.24kg of high-quality compost into the soil to give your young cotton plants a boost.
# * **Water wisely:** Aim for about 1.8 mm of water each day to help roots grow strong.
# * **Early start, big future:** A good yield is in your reach with proper care and attention – let's make that cotton blossom!
# * **Check the weather:**  Keep an eye on the forecast so you can adjust watering as needed."""
# parsed = parse_recommendations(raw_text)
# print(parsed)