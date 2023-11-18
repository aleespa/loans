import dataclasses
from datetime import datetime

import numpy as np
from typing_extensions import Literal


def main():
    loan = Loan(**{'start_date': datetime(2020, 1, 1),
                   'initial_value': 100_000,
                   "payment_frequency": "monthly"})
    print(loan.calculate_principal(datetime(2021, 1, 1)))


@dataclasses.dataclass
class Loan:
    start_date: datetime
    initial_value: float | int | np.ndarray
    payment_frequency: Literal["annual", "semi-annual", "quarterly", "monthly"] | None = None
    payment_dates: list[datetime] | None = None
    interest_rate: float | np.ndarray | list[float] = 0

    def __post_init__(self):
        self.principal = self.initial_value

    def calculate_principal(self,
                            date: datetime) -> float:
        if self.payment_frequency is None and self.payment_dates is None:
            raise Exception("Payment frequency or payment dates not specified")

        return self.principal
