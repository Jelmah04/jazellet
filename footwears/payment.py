from django.shortcuts import redirect, render
import requests
import json
from django.http import HttpResponseRedirect
from jazellet import settings
from decimal import Decimal
from .models import *


def init_payment(email,amount):
    amount = Decimal(amount)*100 # multiply the amount by 100. (from Kobo to Naira)
    url = 'https://api.paystack.co/transaction/initialize'
    headers = {
        'Authorization': 'Bearer '+settings.PAYSTACK_SECRET_KEY,
        'Content-Type' : 'application/json',
        'Accept': 'application/json',
        }
    datum = {
        "email": email,
        "amount": str(amount)
        }
    x = requests.post(url, data=json.dumps(datum), headers=headers)
    if x.status_code != 200:
        return x.json()
    else:
        results = x.json()
        return results
    

