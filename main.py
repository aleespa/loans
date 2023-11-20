from datetime import datetime

from loan_calculator.loan import Loan
from loan_calculator.interest import Interest

loan = Loan(start_date=datetime(2023, 9, 1),
            initial_value=179_596,
            payment_frequency="quarterly",
            payment=5_012.57,
            interest_rate=0.07)

amortization_table = loan.create_amortization()
print(f"Interests paid {amortization_table["Interests"].sum():,.2f}")
loan.add_payment(datetime(2023, 12, 2), 30_000)
amortization_table = loan.create_amortization()
print(f"Interests paid {amortization_table["Interests"].sum():,.2f}")
print(amortization_table)