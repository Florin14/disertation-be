# Id: exceptions.py 202305 11/05/2023
#
# backend
# Copyright (c) 2011-2013 IntegraSoft S.R.L. All rights reserved.
#
# Author: cicada
#   Rev: 202305
#   Date: 11/05/2023
#
# License description...
from project_helpers.error import Error


class ErrorException(Exception):
    def __init__(self, error: Error, message=None, statusCode=500, fields=None):
        self.error = error
        self.message = message
        self.statusCode = statusCode
        self.fields = fields
