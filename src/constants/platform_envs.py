
import os
from enum import Enum


class PlatformEnvs(Enum):
    LOCAL = "local"

    def match(self):
        return self.value == os.environ.get("ENV", "local")
