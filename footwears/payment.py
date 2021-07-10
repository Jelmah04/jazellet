import requests
import json
from django.http import HttpResponseRedirect
from jazellet import settings
from .models import *

def init_payment(username, lastname, email, amount):
    url = 'https://api.paystack.co/transaction/initialize'
    headers = {
        'Authorization': 'Bearer '+settings.PAYSTACK_SECRET_KEY,
        'Content-Type' : 'application/json',
        'Accept': 'application/json',
        }
    datum = {
        "email": email,
        "amount": amount
        }
    x = requests.post(url, data=json.dumps(datum), headers=headers)
    if x.status_code != 200:
        print('not equl to 200')
        print (str(x.status_code))
    else:
        print('x.status is equal 200')
    results = x.json()
    # print('walaaaaaaaaaaaaaaaaaaas3')
    # print(x.status_code)
    # print(results)
    return results
