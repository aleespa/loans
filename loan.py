import dataclasses
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import numpy as np
from typing_extensions import Literal


def main():
    loan = Loan(**{'start_date': datetime(2020, 1, 1),
                   'initial_value': 100_000,
                   "payment_frequency": "monthly",
                   "payment": 1000})
    print(loan.calculate_principal(datetime(2021, 1, 1)))


@dataclasses.dataclass
class Loan:
    start_date: datetime
    initial_value: float | int | np.ndarray
    payment: float | int | np.ndarray = 0
    n_payments: int = 0
    fixed_payments: bool = False
    payment_frequency: Literal["annual", "semi-annual", "quarterly", "monthly"] | None = None
    payment_dates: list[datetime] | None = None
    interest_rate: float | np.ndarray | list[float] = 0

    def __post_init__(self):

        if self.payment_frequency is None and self.payment_dates is None:
            raise Exception("Payment frequency or payment dates not specified")
        elif self.payment_frequency is not None and self.payment_dates is not None:
            raise Exception("Payment frequency and payment dates cannot be specified at the same time")
        elif self.payment_frequency is not None:
            if self.n_payments == 0:
                self.n_payments = int(np.ceil(self.initial_value / self.payment))
            match self.payment_frequency:
                case "annual":
                    self.payment_dates = [self.start_date + relativedelta(months=12 * i)
                                          for i in range(self.n_payments)]
                case "semi-annual":
                    self.payment_dates = [self.start_date + relativedelta(months=6 * i)
                                          for i in range(self.n_payments)]
                case "quarterly":
                    self.payment_dates = [self.start_date + relativedelta(months=3 * i)
                                          for i in range(self.n_payments)]
                case "monthly":
                    self.payment_dates = [self.start_date + relativedelta(months=1 * i)
                                          for i in range(self.n_payments)]
        else:
            pass
        self.principal = self.initial_value

    def calculate_principal(self,
                            date: datetime) -> float:

        principal_value = self.principal
        for payment_date in self.payment_dates:
            if payment_date > date:
                break
            principal_value -= self.payment
        return principal_value
