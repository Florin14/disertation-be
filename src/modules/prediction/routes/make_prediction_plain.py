import joblib
import pandas as pd
import os
# 1) Specifică calea către fișierul .joblib
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models_saved")
MODEL_PATH = f"{MODEL_DIR}/price_model_rf.joblib"

# 2) Încarcă pipeline-ul salvat
#    (pipeline-ul conține atât ColumnTransformer-ul de preprocessing, cât și GBoostRegressor-ul)
model_pipeline = joblib.load(MODEL_PATH)

# 3) Definim un exemplu de date noi (așa cum ar veni de la frontend)
#    Cheile trebuie să fie exact coloanele (features) folosite la antrenament:
#
#    - Numeric: "useful_area", "built_area", "yard_area",
#               "num_rooms", "num_bathrooms", "has_garage", "floor",
#               "ratio_built_useful", "ratio_yard_useful", "ratio_terrace_useful", "ratio_balcony_useful"
#
#    - Categorical: "classification", "land_classification", "city",
#                   "condominium", "has_terrace", "comfort"
#
#    Dacă pipeline-ul tău a fost cel din exemplul anterior, modelul a fost antrenat să
#    prezică price_per_sqm (preț pe mp). Așadar, la final vei înmulți cu useful_area pentru preț.
#
new_data = {
    "useful_area": 120.0,
    "built_area": 130.0,
    "yard_area": 0,
    "num_rooms": 3,
    "num_bathrooms": 2,
    "has_garage": 1,
    "floor": 2,
    # Categoriile:
    "classification": "APARTMENT",
    "land_classification": "RESIDENTIAL",
    "city": "Satu Mare",
    "condominium": "Standard",
    "has_terrace": "Yes",
    "comfort": "High",
}

# 4) Construim un DataFrame cu un singur rând:
df_input = pd.DataFrame([new_data])

# 5) Apelăm modelul pentru a prezice price_per_sqm:
ppsm_pred_array = model_pipeline.predict(df_input)
# Ar trebui să fie un array de forma [valoare_ppsm]
ppsm_pred = float(ppsm_pred_array[0])
# 6) Înmulțim cu suprafața utilă pentru a obține prețul absolut estimat:
predicted_price = ppsm_pred * new_data["useful_area"]

print(f"Predicted price per sqm: {ppsm_pred:.2f} €/mp")
print(f"Predicted total price:   {predicted_price:.2f} €")
