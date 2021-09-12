import requests
from bs4 import BeautifulSoup
import pandas as pd
import regex as re
from flask import Flask, render_template, request, redirect
import urllib
from requests_html import HTML
from requests_html import HTMLSession
import math

#scrapes google
def get_source(url):
    try:
        session = HTMLSession()
        response = session.get(url)
        return response

    except requests.exceptions.RequestException as e:
        print(e)
        
def scrape_google(query):

    query = urllib.parse.quote_plus(query)
    response = get_source("https://www.google.co.uk/search?q=" + query)

    links = list(response.html.absolute_links)
    google_domains = ('https://www.google.', 
                      'https://google.', 
                      'https://webcache.googleusercontent.', 
                      'http://webcache.googleusercontent.', 
                      'https://policies.google.',
                      'https://support.google.',
                      'https://maps.google.')

    for url in links[:]:
        if url.startswith(google_domains):
            links.remove(url)
    links = [x for x in links if 'redfin' in x]
    return links

#calculates mortgage
def calc_mortgage(principal, interest, years):
        '''
        given mortgage loan principal, interest(%) and years to pay
        calculate and return monthly payment amount
        '''
        # monthly rate from annual percentage rate
        interest_rate = interest/(100 * 12)
        # total number of payments
        payment_num = years * 12
        # calculate monthly payment
        payment = principal * \
            (interest_rate/(1-math.pow((1+interest_rate), (-payment_num))))
        return payment

    
def calc_mortgage(principal, interest, years):
        '''
        given mortgage loan principal, interest(%) and years to pay
        calculate and return monthly payment amount
        '''
        # monthly rate from annual percentage rate
        interest_rate = interest/(100 * 12)
        # total number of payments
        payment_num = years * 12
        # calculate monthly payment
        payment = principal * \
            (interest_rate/(1-math.pow((1+interest_rate), (-payment_num))))
        return payment
    
#Calculates Down Payment
def downpayment(price, percent):
        downpayment = (price * (percent/100))
        return downpayment
    
#Calculates Cap Rate
def capRate(income, price):
        return income / price
    
#Calculates Cash On Cash
def cashOnCash(profit, downpayment):
        return profit / downpayment
    
#Calculates Monthly Payment
def monthlypayment(homeInsurance, propertyTaxes, hoa, mortgage, otherExpenses, propertyManagementFee, vacancyRate):
        monthlyPayment = homeInsurance + propertyTaxes + hoa + mortgage + otherExpenses + propertyManagementFee + vacancyRate
        return monthlyPayment
    
#Vacancy Rate
def vacancyRate(state):
    vacancy = pd.read_csv('~\Calc\Data\RentalVacancy.csv')
    vacancy = pd.DataFrame(data = vacancy, columns=['State', 'Vacancy Rate'])
    vacancy = vacancy.loc[vacancy['State'] == state]
    vacancyRate = vacancy['Vacancy Rate']
    index = vacancyRate.index.tolist()
    vacancyRate = float(str(vacancyRate[index[0]]).replace('%', '')) 
    return vacancyRate / 100

app = Flask(__name__)
app.config.from_object(__name__)

@app.route('/', methods=["GET", "POST"])
def home():
    return render_template('index.html')
    
@app.route('/propertyscore', methods=["GET", "POST"])
def propertyscore():
    if request.method == 'POST':
        cashFlow = request.form.get('cashFlow')
        capRate = request.form.get('capRate')
        cashOnCash = request.form.get('cashOnCash')
        percent = request.form.get('downPayment')
        interest = request.form.get('interest')
        years = request.form.get('term')
        propertyManagement = request.form.get('propertyManagement')
        cashFlow = float(cashFlow)
        capRate = float(capRate)
        cashOnCash = float(cashOnCash)
        percent = float(percent)
        interest = float(interest)
        years = int(years)
        propertyManagement = bool(propertyManagement)
        #address
        address = str(request.form.get("address"))
        street = str(address).split(',')[0].strip()
        city = str(address).split(',')[-3].strip()
        state = str(address).split(',')[-2].strip()
        queryAddress = address.replace(',', ' ')
        queryAddress = queryAddress.replace('  ', ' ')
        queryAddress = queryAddress.replace(' ', '+')
        links = scrape_google(queryAddress + '+' + 'redfin')
        concat = state + '/' + city.replace(' ', '-') + '/' + street.split(' ')[0]
        link = [x for x in links if str(concat) in x]
        request_headers = {
            'accept': 
            'text/html, application/xhtml+xml, application/xml;q=0.9, image/webp, image/apng,*/*;q=0.8',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US, en;q=0.8',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
        }
        with requests.Session() as session:
            url = link[0]
            response = session.get(url, headers = request_headers)
        soup = BeautifulSoup(response.content, 'html.parser')

        zipcode = soup.find('meta', {'name' : 'twitter:text:zip'})['content']
        zipcode = str(zipcode)

        #property type
        propertyType = soup.find_all('div', {'class':'keyDetail font-weight-roman font-size-base'})
        propertyType = str(propertyType).split('<div class')
        propertyType = str([x for x in propertyType if 'Property' in x][0]).replace('="keyDetail font-weight-roman font-size-base"><span class="header font-color-gray-light inline-block">Property Type</span><span class="content text-right">','').replace('</span></div>, ', '')

        #beds
        beds = [td.findAll('div') for td in soup.findAll('div', attrs={'class': 'stat-block beds-section'})][0][0]
        beds = beds.text
        beds = int(beds)

        #baths
        baths = float([td.findAll('div') for td in soup.findAll('div', attrs={'class': 'stat-block baths-section'})][0][0].text)
        if (str(baths).split('.')[1] == 0):
            baths = baths.replace('.0', '')
            baths = int(baths)
        else:
            baths = float(baths)

        #sqft
        sqft = int([td.findAll('span') for td in soup.findAll('div', attrs={'class': 'stat-block sqft-section'})][0][0].text.replace(',', ''))

        #price
        price = float([td.findAll('div') for td in soup.findAll('div', attrs={'class': 'stat-block price-section'})][0][0].text.replace('$','').replace(',', ''))

        #property taxes
        propertyTaxes = str(soup.find_all('div', attrs={'class': 'Row col-12 col-xl-6 padding-bottom-medium font-weight-roman font-size-base'})).split('<svg')
        propertyTaxes = str([x for x in propertyTaxes if 'blue' in x][0])
        propertyTaxes = float(re.search(r'([£$€])(\d+(?:\.\d{2})?)', propertyTaxes).groups()[1])

        #home insurance
        homeInsurance = str(soup.find_all('div', attrs={'class': 'Row col-12 col-xl-6 padding-bottom-medium font-weight-roman font-size-base'})).split('<svg')
        homeInsurance = str([x for x in homeInsurance if 'yellow' in x][0])
        homeInsurance = float(re.search(r'([£$€])(\d+(?:\.\d{2})?)', homeInsurance).groups()[1])

        #hoa
        a = str(soup.find_all('div', attrs={'class': 'Row col-12 col-xl-6 padding-bottom-medium font-weight-roman font-size-base'})).split('<svg')
        b = [x for x in a if 'red' in x]
        if len(b) == 0:
            hoa = 0
        elif len(b) >= 1:
            b = str(b[0])
            hoa = float(re.search(r'([£$€])(\d+(?:\.\d{2})?)', b).groups()[1])

        image = soup.find('meta', attrs={'name': 'twitter:image:photo0'})
        if image == None:
            image = 'https://clients.cylindo.com/viewer/3.x/v3.0/documentation/img/not_found.gif'
        else:
            image = image.get('content')

        #calculates mortgage & downpayment
        downPayment = downpayment(price, percent)

        # mortgage loan principal
        principal = price - downPayment

        if interest == None:
            interest = 4

        # calculate monthly payment amount
        mortgage = float(round(calc_mortgage(principal, interest, years), 2))

        if beds >= 6:
            beds1 = 6

        #long term
        address0 = street.replace(' ', '-') + '-' + city.replace(' ', '-') + '-' + state.lower().replace(' ',  '-')+ '-' + zipcode

        url = "https://www.zillow.com/rental-manager/price-my-rental/results/" + address0 + '/'

        results = requests.get(url)
        soup1 = BeautifulSoup(results.content, 'html.parser')

        traditionalincome = soup1.find('h2', {'class': 'Text-c11n-8-23-1__aiai24-0 cpSRFk'}).text.replace('$', '').replace(',', '').replace('/moEdit', '')

        if(len(traditionalincome) == 0):
            traditionalincome = None
        else:
            traditionalincome = float(traditionalincome)

        otherExpenses = 0

        if propertyManagement == True:
            propertyManagementFee = traditionalincome * .1
        else:
            propertyManagementFee = 0

        vacancyrate = traditionalincome * vacancyRate(state)

        monthlyPayment = monthlypayment(homeInsurance, propertyTaxes, hoa, mortgage, otherExpenses, propertyManagementFee, vacancyrate)
        monthlyPayment = float(monthlyPayment)
        traditionalProfit = traditionalincome - monthlyPayment
        traditionalCapRate = round((traditionalincome / price) * 100, 2)
        traditionalCashOnCash = round((traditionalProfit / downPayment)* 100, 2)

        #short term
        with requests.Session() as session:
            url= "https://www.mashvisor.com/cities/" + state.lower().replace(' ', '') + "/" + city.replace(' ', '-') + "-investment-property-guide"
            response = session.get(url, headers = request_headers)

        soup2 = BeautifulSoup(response.content, 'html.parser')

        #price/bed
        if (beds <= 1):
            airbnbincome = pd.read_html(url) # Returns list of all tables on page
            airbnbincome = float(airbnbincome[0].iloc[0].iloc[1].replace('$ ', '').replace(',', ''))
        elif (beds == 2):
            airbnbincome = pd.read_html(url) # Returns list of all tables on page
            airbnbincome = float(airbnbincome[0].iloc[0].iloc[2].replace('$ ', '').replace(',', ''))
        elif (beds == 3):
            airbnbincome = pd.read_html(url) # Returns list of all tables on page
            airbnbincome = float(airbnbincome[0].iloc[0].iloc[3].replace('$ ', '').replace(',', ''))
        elif (beds >= 4):
            airbnbincome = pd.read_html(url) # Returns list of all tables on page
            airbnbincome = float(airbnbincome[0].iloc[0].iloc[4].replace('$ ', '').replace(',', ''))
        else:
            airbnbincome = None

        airbnbProfit = airbnbincome - monthlyPayment
        airbnbCapRate = round((airbnbincome / price) * 100, 2)
        airbnbCashOnCash = round((airbnbProfit / downPayment) * 100, 2)

        #closing costs & all in
        closingCosts = principal * .05
        allin = downPayment + closingCosts

        #defines rules
        fiftyPercent = traditionalincome / 2
        breakEvenLT = (allin / traditionalProfit) / 12
        breakEvenST = (allin / airbnbProfit) / 12
        twoPercent = False

        #output
        price = "${:,.2f}".format(float(price))
        stcashFlow = "${:,.2f}".format(airbnbProfit)
        ltcashFlow = "${:,.2f}".format(traditionalProfit)
        monthlyPayment = "${:,.2f}".format(monthlyPayment)
        stcapRate = "{:,.2f}%".format(airbnbCapRate)
        ltcapRate = "{:,.2f}%".format(traditionalCapRate)
        stcashOnCash = "{:,.2f}%".format(airbnbCashOnCash)
        ltcashOnCash = "{:,.2f}%".format(traditionalCashOnCash)

        if traditionalProfit <= 0:
            breakEvenLT = "Never"
        else:
            breakEvenLT = "{:.2f} Year(s)".format(breakEvenLT)

        if airbnbProfit <= 0:
            breakEvenST = "Never"
        else:
            breakEvenST = "{:.2f} Year(s)".format(breakEvenST)

        if twoPercent == True:
            twoPercent = price * .02

        if (traditionalincome == twoPercent):
            twoPercent = True
        else:
            twoPercent = False

        if traditionalProfit != None:
            traditionalProfitString = "${:.2f}".format(traditionalProfit)

        if airbnbProfit != None:
            airbnbProfitString = "${:.2f}".format(airbnbProfit)

        if traditionalCapRate != None:
            traditionalCapRateString = "{:.2f}%".format(traditionalCapRate)

        if airbnbCapRate != None:
            airbnbCapRateString = "{:.2f}%".format(airbnbCapRate)

        if traditionalCashOnCash != None:
            traditionalCashOnCashString = "{:.2f}%".format(traditionalCashOnCash)

        if airbnbCashOnCash != None:
            airbnbCashOnCashString = "{:.2f}%".format(airbnbCashOnCash)

        traditionalincomeString = "${:,.2f}".format(traditionalincome)
        airbnbincomeString = "${:,.2f}".format(airbnbincome)
        fiftyPercentString = "${:,.2f}".format(fiftyPercent)

        if (airbnbProfit >= cashFlow) and (airbnbCapRate >= capRate) and (airbnbCashOnCash >= cashOnCash) and (twoPercent == True):
            airbnbGoodDeal = 1
        else:
            airbnbGoodDeal = False

        if(traditionalProfit >= cashFlow) and (traditionalCapRate >= capRate) and (traditionalCashOnCash >= cashOnCash) and (twoPercent == True):
            traditionalGoodDeal = 1
        elif(traditionalProfit >= cashFlow) or (traditionalCapRate >= capRate) or (traditionalCashOnCash >= cashOnCash) and (twoPercent == True):
            traditionalGoodDeal = 2
        elif(traditionalProfit >= cashFlow):
            traditionalGoodDeal = 3
        else:
            traditionalGoodDeal = 4

        if ((airbnbProfit >= cashFlow) and (airbnbCapRate >= capRate) and (airbnbCashOnCash >= cashOnCash)):
            airbnbGoodDeal = True
        else:
            airbnbGoodDeal = False

        if ((traditionalProfit >= cashFlow) and (traditionalCapRate >= capRate) and (traditionalCashOnCash >= cashOnCash)):
            traditionalGoodDeal = True
        else:
            traditionalGoodDeal = False

        #check or x for financials
        if (cashFlow >= traditionalProfit):
            cfcheck = True
        else:
            cfcheck = False
        
        if (capRate >= traditionalCapRate):
            crcheck = True
        else:
            crcheck = False
            
        if (cashOnCash >= traditionalCashOnCash):
            coccheck = True
        else:
            coccheck = False
            
            
        if (cashFlow >= airbnbProfit):
            stcfcheck = True
        else:
            stcfcheck = False
        
        if (capRate >= airbnbCapRate):
            stcrcheck = True
        else:
            stcrcheck = False
            
        if (cashOnCash >= airbnbCashOnCash):
            stcoccheck = True
        else:
            stcoccheck = False
        
        if cfcheck == True: 
            cfcheck = "https://image.flaticon.com/icons/png/512/443/443138.png"
            cfcheck = "https://image.flaticon.com/icons/png/512/443/443152.png"
        
        if traditionalGoodDeal == 1:
            ltstar1 = 'fa fa-star checked'
            ltstar2 = 'fa fa-star checked'
            ltstar3 = 'fa fa-star checked'
            ltstar4 = 'fa fa-star checked'
            ltstar5 = 'fa fa-star checked'
        elif traditionalGoodDeal == 2:
            ltstar1 = 'fa fa-star checked'
            ltstar2 = 'fa fa-star checked'
            ltstar3 = 'fa fa-star checked'
            ltstar4 = 'fa fa-star checked'
            ltstar5 = 'fa fa-star'
        elif traditionalGoodDeal == 3:
            ltstar1 = 'fa fa-star checked'
            ltstar2 = 'fa fa-star checked'
            ltstar3 = 'fa fa-star checked'
            ltstar4 = 'fa fa-star'
            ltstar5 = 'fa fa-star'
        elif traditionalGoodDeal == 4:
            ltstar1 = 'fa fa-star checked'
            ltstar2 = 'fa fa-star checked'
            ltstar3 = 'fa fa-star'
            ltstar4 = 'fa fa-star'
            ltstar5 = 'fa fa-star'
        else:
            ltstar1 = 'fa fa-star checked'
            ltstar2 = 'fa fa-star'
            ltstar3 = 'fa fa-star'
            ltstar4 = 'fa fa-star'
            ltstar5 = 'fa fa-star'
            
        if airbnbGoodDeal == 1:
            ststar1 = 'fa fa-star checked'
            ststar2 = 'fa fa-star checked'
            ststar3 = 'fa fa-star checked'
            ststar4 = 'fa fa-star checked'
            ststar5 = 'fa fa-star checked'
        elif airbnbGoodDeal == 2:
            ststar1 = 'fa fa-star checked'
            ststar2 = 'fa fa-star checked'
            ststar3 = 'fa fa-star checked'
            ststar4 = 'fa fa-star checked'
            ststar5 = 'fa fa-star'
        elif airbnbGoodDeal == 3:
            ststar1 = 'fa fa-star checked'
            ststar2 = 'fa fa-star checked'
            ststar3 = 'fa fa-star checked'
            ststar4 = 'fa fa-star'
            ststar5 = 'fa fa-star'
        elif airbnbGoodDeal == 4:
            ststar1 = 'fa fa-star checked'
            ststar2 = 'fa fa-star checked'
            ststar3 = 'fa fa-star'
            ststar4 = 'fa fa-star'
            ststar5 = 'fa fa-star'
        else:
            ststar1 = 'fa fa-star checked'
            ststar2 = 'fa fa-star'
            ststar3 = 'fa fa-star'
            ststar4 = 'fa fa-star'
            ststar5 = 'fa fa-star'
            
    return render_template('propertyscore.html', image = image, address = address, street = street, propertyType = propertyType, beds = beds, baths = baths, sqft = sqft, price = price, monthlyPayment = monthlyPayment, stcashFlow = stcashFlow, ltcashFlow = ltcashFlow, stcapRate = stcapRate, ltcapRate = ltcapRate, stcashOnCash = stcashOnCash, ltcashOnCash = ltcashOnCash, breakEvenLT = breakEvenLT, breakEvenST = breakEvenST, ststar1 = ststar1 , ststar2 = ststar2, ststar3 = ststar3, ststar4 = ststar4, ststar5 = ststar5, ltstar1 = ltstar1 , ltstar2 = ltstar2, ltstar3 = ltstar3, ltstar4 = ltstar4, ltstar5 = ltstar5, cfcheck = cfcheck, stcfcheck = stcfcheck, crcheck = crcheck, stcrcheck = stcrcheck, coccheck = coccheck, stcoccheck = stcoccheck)

@app.route('/locationscore', methods=["GET", "POST"])
def locationscore():
    #address
    address = request.form.get("address", type=str)
    street = str(address).split(',')[0].strip()
    city = str(address).split(',')[-3].strip()
    state = str(address).split(',')[-2].strip()
    return render_template('locationscore.html', city = city, state = state)

if __name__ == '__main__':
    app.debug=True
    app.run()