# Id: get_storage.py 202307 13/07/2023
#
# backend
# Copyright (c) 2011-2013 IntegraSoft S.R.L. All rights reserved.
#
# Author: cicada
#   Rev: 202307
#   Date: 13/07/2023
#
# License description...
from gridfs import GridFSBucket
from extensions.mongo import db


class GetStorage:
    def __call__(self, folder: str):
        storage = GridFSBucket(db, bucket_name=folder)
        return storage
