import dataclasses
from datetime import datetime, timedelta

import pandas as pd
from dateutil.relativedelta import relativedelta

import numpy as np
from typing_extensions import Literal

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
pd.options.display.float_format = '{:,.2f}'.format


@dataclasses.dataclass
class Loan:
    start_date: datetime
    initial_value: float | int | np.ndarray
    payment: float | int | list[float | int] = 0
    n_payments: int = 0
    fixed_payments: bool = False
    payment_frequency: Literal["annual", "semi-annual", "quarterly", "monthly"] | None = None
    payment_dates: list[datetime] | None = None
    interest_rate: float | np.ndarray | list[float] = 0
    additional_payment: dict = dataclasses.field(default_factory=dict)

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
                                          for i in range(1, self.n_payments + 1)]
                case "semi-annual":
                    self.payment_dates = [self.start_date + relativedelta(months=6 * i)
                                          for i in range(1, self.n_payments + 1)]
                case "quarterly":
                    self.payment_dates = [self.start_date + relativedelta(months=3 * i)
                                          for i in range(1, self.n_payments + 1)]
                case "monthly":
                    self.payment_dates = [self.start_date + relativedelta(months=1 * i)
                                          for i in range(1, self.n_payments + 1)]
        else:
            pass
        self.principal = self.initial_value

    def calculate_principal(self,
                            date: datetime) -> float:

        principal_value = self.principal
        for payment_number in range(self.n_payments):
            if self.payment_dates[payment_number] > date:
                break
            principal_value -= self.payment[payment_number]
        return max(0, principal_value)

    def calculate_principal_payment(self,
                                    payment_number: int):
        if payment_number == 0:
            return 0
        principal_value = self.principal
        for payment_number in range(payment_number):
            principal_value -= self.payment[payment_number]
        if principal_value < self.payment[payment_number]:
            return principal_value
        else:
            return self.payment[payment_number]

    def calculate_interest_payment(self,
                                   payment_number: int):
        principal_value = self.principal
        for payment_number in range(payment_number):
            principal_value -= self.payment[payment_number]
        if principal_value < self.payment[payment_number]:
            return principal_value
        else:
            return self.payment[payment_number]

    def calculate_interest(self,
                           date_0,
                           date_1):
        return ((date_0 - date_1).days / 365) * self.interest_rate

    def create_amortization(self) -> pd.DataFrame:
        table = pd.DataFrame(columns=["Principal"],
                             index=self.payment_dates + list(self.additional_payment.keys()))
        table.loc[self.start_date, "Principal"] = self.initial_value
        table.loc[self.start_date, "Principal payment"] = 0
        table.loc[self.start_date, "Interests"] = 0
        table.loc[:, "Additional"] = False
        table.loc[list(self.additional_payment.keys()), "Additional"] = True
        table = table.sort_index()
        previous_date = self.start_date
        for i, date in enumerate(table.index[1:]):
            table.loc[date, "Interests"] = (table.loc[previous_date, "Principal"]
                                            * self.calculate_interest(date, previous_date))
            if table.loc[date, "Additional"]:
                table.loc[date, "Principal payment"] = self.additional_payment[date] - table.loc[date, "Interests"]
            else:
                table.loc[date, "Principal payment"] = min(self.payment, table.loc[previous_date, "Principal"])
            table.loc[date, "Principal"] = (table.loc[previous_date, "Principal"]
                                            - table.loc[date, "Principal payment"])
            if table.loc[date, "Additional"] & (~self.fixed_payments):
                self.payment = table.loc[date, "Principal"] / (self.n_payments - i)

            previous_date = date
        table.loc[:, "Total payment"] = (table.loc[:, "Principal payment"]
                                         + table.loc[:, "Interests"])
        return (table
                .sort_index()
                .drop(columns="Additional"))

    def add_payment(self,
                    date,
                    amount):
        self.additional_payment |= {date: amount}
