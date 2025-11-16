def prepare_model_output(preds:dict)->dict:
    return {
        "crop_stage": str(preds["crop_stage"]),
        "required_n": preds["fertilizer"]["nutrient_needs"]["N_need"],
        "required_p": preds["fertilizer"]["nutrient_needs"]["P_need"],
        "required_k": preds["fertilizer"]["nutrient_needs"]["K_need"],
        "irrigation": float(preds["irrigation"]),
        "yield": float(preds["yield"])
    }