import pandas as pd

def prepare_input_for_prediction(payload: dict) -> pd.DataFrame:
    """
    Transforms the payload dictionary into a DataFrame with the expected columns.
    """
    # Define the expected columns for the model
    expected_columns = [
        "address", "city", "useful_area", "classification", "num_rooms",
        "num_bathrooms", "num_kitchens", "has_parking_space",
        "num_garages", "useful_area_total", "built_area", "built_year", "land_area", "yard_area",
        "has_terrace", "has_balconies", "floor", "structure",
        "comfort", "condominium", "price", "land_classification", "street_frontage"
    ]

    # Create a DataFrame from the payload
    df = pd.DataFrame([payload])

    # Ensure all expected columns are present
    for col in expected_columns:
        if col not in df.columns:
            raise ValueError(f"Missing column: {col}")

    # Return the DataFrame with the expected columns
    return df[expected_columns]