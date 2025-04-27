# Id: scheduler_model.py 202307 19/07/2023
#
# backend
# Copyright (c) 2011-2013 IntegraSoft S.R.L. All rights reserved.
#
# Author: cicada
#   Rev: 202307
#   Date: 19/07/2023
#
# License description...
from extensions import SqlBaseModel
from sqlalchemy import String, Column, Float
from sqlalchemy.dialects.postgresql import BYTEA


class ManualSchedulerModel(SqlBaseModel):
    __tablename__ = "manual_jobs"
    id = Column(String(191), primary_key=True)
    next_run_time = Column(Float)
    job_state = Column(BYTEA)
