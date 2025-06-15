from datetime import datetime

from extensions import SessionLocal
from modules.listing.models.performance_model import PerformanceModel
from modules.listing.models.performance_schemas import PerformanceCreate, HistoryCreate
from modules.price_history.models.price_history_model import PriceHistoryModel


def create_performance(perf: PerformanceCreate) -> PerformanceModel:
    with SessionLocal() as db:
        db_obj = PerformanceModel(
            model_name=perf.model_name,
            mae=perf.mae,
            rmse=perf.rmse,
            r2=perf.r2,
            created_at=perf.created_at or datetime.now(),
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


def create_history(perf: HistoryCreate) -> PerformanceModel:
    with SessionLocal() as db:
        db_obj = PriceHistoryModel(
            base_location=perf.base_location,
            price_per_sqm=perf.price_per_sqm,
            predicted_price=perf.predicted_price,
            num_rooms=perf.num_rooms,
            city=perf.city,
            user_id=perf.user_id,
            location_raw=perf.location_raw,
            useful_area=perf.useful_area,
            total_price=perf.total_price,
            latitude=perf.latitude,
            longitude=perf.longitude)
        db.add(db_obj)
        db.commit()
        return db_obj
