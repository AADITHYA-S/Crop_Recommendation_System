import ollama
from utils.text_parser import parse_recommendations

def generate_recommendations(preds,crop,lang="en"):
    """
        Generate a simple, farmer friendly recommendations using local LLM(via ollama)
    """

    prompt=f"""
        You are a local agricultural advisor.
        Based on the following crop data, write a short,clear,farmer friendly,advice in {lang}:

        Crop: {crop}
        Stage: {preds["crop_stage"]}
        Fertilizer_Name: {preds["fertilizer"]["fertilizer_name"]}
        Fertilizer_quantity:{preds["fertilizer"]["quantity_kg_per_acre"]} (Kg/acre)
        Irrigation: {preds["irrigation"]:.1f} mm/day
        Predicted Yield: {preds["yield"]:.1f} kg/acre

        Keep sentences short,avoid technical words.
        Respond in 3-4 bullet points only.
        """
    response=ollama.chat(
            model="gemma2:2b",
            messages=[{'role':'user','content':prompt}]
        )
    # parsed = parse_recommendations(response["message"]["content"])
    return response["message"]["content"]