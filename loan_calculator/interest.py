import dataclasses
from typing import Literal

import numpy as np


@dataclasses.dataclass
class Interest:
    interest_rate: float | np.ndarray
    frequency: Literal["annual", "monthly"] = "annual"
