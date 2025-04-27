from extensions import SqlBaseModel
from sqlalchemy import String, Column, Float
from sqlalchemy.dialects.postgresql import BYTEA


class ManualSchedulerModel(SqlBaseModel):
    __tablename__ = "manual_jobs"
    id = Column(String(191), primary_key=True)
    next_run_time = Column(Float)
    job_state = Column(BYTEA)
