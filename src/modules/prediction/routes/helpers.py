import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from modules.prediction.models import PredictionAdd, PredictionsModel
from modules.listing.models.listing_model import ListingModel

engine = create_engine("postgresql://postgres:1234@localhost:5432/disertation_db")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def load_listings_as_dataframe(
) -> pd.DataFrame:
    """
    1) Creează o sesiune SQLAlchemy
    2) Construiește același query pe ListingModel pe care îl faci în endpoint
       get_all_listing (fără a aplica .all() – pentru că vrem să-l trimitem
       către pandas.read_sql)
    3) Folosește pandas.read_sql(...) pentru a obține un DataFrame
       din acel query.statement
    4) Returnează DataFrame-ul.
    """

    db = SessionLocal()
    try:
        # 1) Pornim query-ul
        listing_query = db.query(ListingModel)

        # 4) Extragem structura de SELECT din query către un DataFrame
        #    Pandas poate primi un obiect SQLAlchemy Query prin `query.statement`
        #    și un `bind` (engine-ul)
        df = pd.read_sql(listing_query.statement, con=db.bind)

        return df

    finally:
        db.close()


def create_prediction(
    db,
    pred_add: PredictionAdd,
    pred_price: float
) -> PredictionsModel:
    """
    Crează un PredictionsModel din datele din pred_add + pred_price
    și îl salvează în baza de date. Returnează obiectul SQLAlchemy cu id-ul populat.
    """
    data = pred_add.dict()
    data["predicted_price"] = pred_price

    db_pred = PredictionsModel(**data)
    db.add(db_pred)
    db.commit()
    db.refresh(db_pred)
    return db_pred

def get_prediction(db, prediction_id: int) -> PredictionsModel:
    """
    Întoarce PredictionsModel cu id = prediction_id sau None dacă nu există.
    """
    return db.query(PredictionsModel).filter(PredictionsModel.id == prediction_id).first()
