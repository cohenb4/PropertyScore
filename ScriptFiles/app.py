import requests
from flask import Flask, render_template, request, redirect
import math
from datetime import date
import pandas as pd
import numpy_financial as npf

def DollarFormat(dol):
    return "${:,.2f}".format(dol)

def YearFormat(year):
    return "{:,} years".format(year)

def PercFormat(perc):
    return "{:,.2f}%".format(perc)

def EmptyStar():
    return "fa fa-star"

def GoldStar():
    return "fa fa-star color-gold"

app = Flask(__name__)
app.config.from_object(__name__)

@app.route('/', methods = ["GET", "POST"])
def home():
    if request.method == "POST":
        address = str(request.form.get("address"))
        downPayment = float(request.form.get("downPayment")) / 100
        interestRate = float(request.form.get("interestRate")) / 100 / 12
        term = int(request.form.get("term"))
        cashFlow = float(request.form.get("cashFlow"))
        capRate = float(request.form.get("capRate")) / 100
        cashOnCash = float(request.form.get("cashOnCash")) / 100
        
    return render_template('form.html')

@app.route('/propertyscore', methods=["GET", "POST"])
def propertyscore():
    #inputs
    address = str(request.form.get("address"))
    downPayment = float(request.form.get("downPayment")) / 100
    interestRate = float(request.form.get("interestRate")) / 100 / 12
    term = int(request.form.get("term"))
    cashFlow = float(request.form.get("cashFlow"))
    capRate = float(request.form.get("capRate")) / 100
    cashOnCash = float(request.form.get("cashOnCash")) / 100
    price = 100000
    
    #formulas
    #downpayment = downpayment percentage * price
    downPayment *= price
    #loan = price - downpayment
    loan = price - downPayment
    mortgage = npf.pmt(interestRate, term * 12, -loan)
    allin = downPayment + price * .05
    
    #header
    address = address.replace('+', ' ')
    
    #cards
    beds = 2
    baths = 3
    sqft = 1000
    propertyType = "Single Family"
    
    #expenses
    ltExpenses = 10
    stExpenses = 10
    insurance = 10
    taxes = 10
    hoa = 10
    monthlyPayment = mortgage + insurance + taxes + hoa
    
    #income
    ltIncome = 1000
    stIncome = 1000
    
    #financial table
    ltCashFlow = ltIncome - monthlyPayment
    stCashFlow = stIncome - monthlyPayment
    ltCapRate = ltIncome / price
    stCapRate = stIncome / price
    ltCashOnCash = ltIncome / allin
    stCashOnCash = stIncome / allin
    equity = ((.035 * term * price) + price) - downPayment
    ltROI = equity + (ltCashFlow * term * 12)
    stROI = equity + (stCashFlow * term * 12)
    breakEvenLT = round((allin / ltCashFlow / 12), 1)
    breakEvenST = round((allin / stCashFlow / 12), 1)
    
    if ltCashFlow >= cashFlow:
        ltCashFlowicon = "fa fa-check"
    else:
        ltCashFlowicon = "fa fa-remove"

    if stCashFlow >= cashFlow:
        stCashFlowicon = "fa fa-check"
    else:
        stCashFlowicon = "fa fa-remove"
        
    if ltCapRate >= capRate:
        ltCapRateicon = "fa fa-check"
    else:
        ltCapRateicon = "fa fa-remove"

    if stCapRate >= cashFlow:
        stCapRateicon = "fa fa-check"
    else:
        stCapRateicon = "fa fa-remove"
        
    if ltCashOnCash >= cashOnCash:
        ltCOCicon = "fa fa-check"
    else:
        ltCOCicon = "fa fa-remove"

    if stCashOnCash >= cashOnCash:
        stCOCicon = "fa fa-check"
    else:
        stCOCicon = "fa fa-remove"
    
    score = 'A'
        
    if score == 'A':
        star1, star2, star3, star4, star5 = GoldStar(), GoldStar(), GoldStar(), GoldStar(), GoldStar()
    
    elif score == 'B':
        star1, star2, star3, star4, star5 = GoldStar(), GoldStar(), GoldStar(), GoldStar(), EmptyStar()
        
    elif score == 'C':
        star1, star2, star3, star4, star5 = GoldStar(), GoldStar(), GoldStar(), EmptyStar(), EmptyStar()
        
    elif score == 'D':
        star1, star2, star3, star4, star5 = GoldStar(), GoldStar(), EmptyStar(), EmptyStar(), EmptyStar()

    return render_template('index.html', address = address, beds = beds, baths = baths, sqft = "{:,d}".format(sqft), propertyType = propertyType, ltCashFlow = DollarFormat(ltCashFlow), stCashFlow = DollarFormat(stCashFlow), price = DollarFormat(price), monthlyPayment = DollarFormat(monthlyPayment), ltCapRate = PercFormat(ltCapRate), stCapRate = PercFormat(stCapRate), ltCashOnCash = PercFormat(ltCashOnCash), stCashOnCash = PercFormat(stCashOnCash), breakEvenLT = YearFormat(breakEvenLT), breakEvenST = YearFormat(breakEvenST), ltIncome = DollarFormat(ltIncome), stIncome = DollarFormat(stIncome), mortgage = DollarFormat(mortgage), ltROI = DollarFormat(ltROI), stROI = DollarFormat(stROI), term = term, ltCashFlowicon = ltCashFlowicon, stCashFlowicon = stCashFlowicon, ltCapRateicon = ltCapRateicon, stCapRateicon = stCapRateicon, ltCOCicon = ltCOCicon, stCOCicon = stCOCicon, star1 = star1, star2 = star2, star3 = star3, star4 = star4, star5 = star5)

if __name__ == '__main__':
    app.debug=True
    app.run()