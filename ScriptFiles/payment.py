class Payments:
    downPayment *= price
    loan = price - downPayment
    mortgage = npf.pmt(interestRate, term * 12, -loan)
    allin = downPayment + price * .05