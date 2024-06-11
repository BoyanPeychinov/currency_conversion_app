import sys
import json
import requests
from datetime import datetime


INVALID_DATE_MSG = "Please enter valid date in the format YYYY-MM-DD: "
INVALID_AMOUNT_MSG = "Please enter a valid amount: "
INVALID_CURRENCY_MSG = "Please enter a valid currency code: "


api_key = ""

with open("config.json", "r") as file:
    data = json.load(file)
    api_key = data["api_key"]
    

used_currencies = {}


def get_currency_rates(currency):
    url = f"https://api.fastforex.io/fetch-all?from={currency}&api_key={api_key}"
    headers = {"accept": "application/json"}
    response = requests.get(url, headers)
    rates = response.json()["results"]
    return rates

def get_currency_codes():
    url = f"https://api.fastforex.io/currencies?api_key={api_key}"
    headers = {"accept": "application/json"}
    response = requests.get(url, headers)
    data = response.json()["currencies"]
    codes = list(data.keys())
    return codes

def get_valid_input(msg, validator, value, *args):
    while True:
        
        if value.isalpha() and value.upper() == "END":
            exit()
        
        value = validator(value, *args)
        
        if value:
            break
        else:
            value = input(msg)
            
    
    return value
        
def validate_date_input(date, *args):
    format = "%Y-%m-%d"
    
    try:
        is_date_valid = bool(datetime.strptime(date, format))
        if is_date_valid:
            return date
    except ValueError:
        return False

def validate_amount_input(amount, *args):
    try:
        __, frac = amount.split(".")

        if len(frac) != 2:
            return False
        
        amount = float(amount)
        
        if amount <= 0:
            return False    
        
        return amount
    except ValueError:
        return False
        
def validate_currency_input(currency, *args):
    codes = list(*args)
    
    if not currency.isalpha():
        return False
    
    currency = currency.upper()
    
    if len(currency) != 3:
        return False
    
    if currency not in codes:
        return False
                
    return currency

def convert_amount(rate, amount):
    result = amount * rate
    return round(result, 2)

def write_conversion_to_json(conversion, filename="conversions.json"):
    with open(filename, "w") as file:
        json.dump(conversion, file, indent=4)


conversion_date = sys.argv[1]

currencies_codes = get_currency_codes()

while True:
    
    conversion = {}
    
    date = get_valid_input(INVALID_DATE_MSG, validate_date_input, conversion_date)
    
    conversion["date"] = date
    
    amount = input("Enter amount: ")
    
    amount = get_valid_input(INVALID_AMOUNT_MSG, validate_amount_input, amount)
    
    conversion["amount"] = amount
    
    base_currency = input("Enter base currency: ")
     
    base_currency = get_valid_input(INVALID_CURRENCY_MSG, validate_currency_input, base_currency, currencies_codes)
    
    conversion["base_currency"] = base_currency
    
    target_currency = input("Enter target currency: ")
    
    
    target_currency = get_valid_input(INVALID_CURRENCY_MSG, validate_currency_input, target_currency, currencies_codes)
    
    conversion["target_currency"] = target_currency
 
    if base_currency in used_currencies:
        rate = used_currencies[base_currency][target_currency]
    else:
        rates = get_currency_rates(base_currency)
        used_currencies[base_currency] = rates
        rate = rates[target_currency]
    
    converted_amount = convert_amount(rate, amount)
    conversion["converted_amount"] = converted_amount
    
    with open("conversions.json") as json_file:
        try:
            data = json.load(json_file)
        except json.JSONDecodeError:
            data = []   
        data.append(conversion)
    
    write_conversion_to_json(data)
    
    conversion_date = input("Date: ")

    

    