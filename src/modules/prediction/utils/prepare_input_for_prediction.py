import pandas as pd


def prepare_input_for_prediction(data: dict) -> pd.DataFrame:
    """
    - Primește un dict (payload.dict()) care conține strict
      aceleași chei pe care le-ai folosit la antrenament (numeric + categoric).
    - Construiește un DataFrame cu un singur rând.
    - Returnează DataFrame-ul care va fi pus direct în model_pipeline.predict().

    Exemplu:
        dacă data = {
            "useful_area": 55.0,
            "num_rooms": 2,
            "num_bathrooms": 1,
            "num_garages": 0,
            "floor": 3,
            "street_frontage": 8.5,
            "built_area": 65.0,
            "classification": "Casă",
            "land_classification": "Rezidențial",
            "city": "Cluj-Napoca",
            # …
        }
        atunci DataFrame-ul va fi:
                    useful_area  num_rooms  num_bathrooms  num_garages  floor  street_frontage  built_area  classification  land_classification        city
        0                   55          2               1            0      3               8.5        65.0          Casă     Rezidențial  Cluj-Napoca
    """
    # 1) Construiește un DataFrame cu exact același set de coloane
    #    ca la antrenament. Dacă lipsește vreuna, Pandas va pune NaN, iar pipeline-ul
    #    va face imputarea cu 0 / “missing” (după cum ai definit la antrenament).
    print(data)
    df = pd.DataFrame([data])

    # 2) (Opțional) Poți completa valori implicite pentru coloane care nu există
    #    în payload, ex.:
    # for col in ["useful_area", "num_rooms", ...]:
    #     if col not in df.columns:
    #         df[col] = pd.NA

    return df