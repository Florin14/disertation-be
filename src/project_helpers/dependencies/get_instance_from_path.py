# Id: get_instance_by_id.py 202305 12/05/2023
#
# backend
# Copyright (c) 2011-2013 IntegraSoft S.R.L. All rights reserved.
#
# Author: cicada
#   Rev: 202305
#   Date: 12/05/2023
#
# License description...
from typing import Optional, Union

from fastapi import Depends
from sqlalchemy.orm import Session
from extensions import get_db
from project_helpers.exceptions import ErrorException
from project_helpers.error import Error


class GetInstanceFromPath:
    def __init__(self, instanceModel):
        self.instanceModel = instanceModel

    def __call__(self, id: Union[int, str] = None, db: Session = Depends(get_db)):
        instance = None
        if id is not None:
            instance = db.query(self.instanceModel).get(id)
        if instance is None:
            raise ErrorException(error=Error.DB_MODEL_INSTANCE_DOES_NOT_EXISTS)
        return instance
