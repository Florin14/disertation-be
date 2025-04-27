from extensions import SqlBaseModel
from sqlalchemy import String, Column, Float
from sqlalchemy.dialects.postgresql import BYTEA


class AutoSchedulerModel(SqlBaseModel):
    __tablename__ = "auto_jobs"
    id = Column(String(191), primary_key=True)
    next_run_time = Column(Float)
    job_state = Column(BYTEA)
