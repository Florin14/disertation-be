from datetime import datetime
from sqlalchemy.orm import Session

from extensions import SessionLocal
from modules.listing.models.performance_model import PerformanceModel
from modules.listing.models.performance_schemas import PerformanceCreate


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