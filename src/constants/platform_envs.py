
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
