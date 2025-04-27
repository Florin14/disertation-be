# Id: environments.py 202307 12/07/2023
#
# backend
# Copyright (c) 2011-2013 IntegraSoft S.R.L. All rights reserved.
#
# Author: cicada
#   Rev: 202307
#   Date: 12/07/2023
#
# License description...
import os
from enum import Enum


class PlatformEnvs(Enum):
    LOCAL = "local"
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PREPRODUCTION = "preproduction"
    PRODUCTION = "production"

    def match(self):
        return self.value == os.environ.get("ENV", "local")
