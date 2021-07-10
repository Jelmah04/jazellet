from rest_framework import response
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests

from django.http import response
from django.http.response import JsonResponse
from django.http import HttpResponseRedirect
from .payment import init_payment
from django.shortcuts import render
import secrets
# import uuid
from django.shortcuts import render,redirect
from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login,logout,authenticate
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.forms import UserCreationForm
from .forms import UserRegisterForm


# Create your views here.
def home(request):
    featured = Product.objects.filter(featured=True).order_by('id').reverse()[:6]
    context = {
        'featured': featured
    }
    return render(request, 'footwears/home.html', context)

def contact(request):
    return render(request, 'footwears/contact.html')

def allfootwears(request):
    products = Product.objects.all()
    context = {
        'products' : products
    }
    return render(request, 'footwears/allfootwears.html', context)

def allheadwears(request):
    return render(request, 'footwears/allheadwears.html')

@login_required
def single(request, prod_id):
    single = Product.objects.get(pk=prod_id)
    context = {
        'single' : single
    }
    return render(request, 'footwears/single.html', context)

def webhook (request):
	if request.method == 'POST':
		email = request.POST['email']
		amount = request.POST['prodamount']
		username = request.user.username
		lastname = request.user.last_name
		amount = int(amount)*100

		# print(email)print(username)print(lastname)print(amount)
		initialized = init_payment(username, lastname, email, amount)
		print(initialized["data"]["authorization_url"])
		amount = amount/100
		instance = PayHistory.objects.create(amount=amount, user=request.user, paystack_charge_id=initialized['data']['reference'], paystack_access_code=initialized['data']['access_code'])

		# wallet = UserWallet.objects.get(user=request.user)
		# old_amt = wallet + amount
		# wallet.save()
		
		link = initialized['data']['authorization_url']
		return HttpResponseRedirect(link)
	return render (request, 'webhook.html')


@csrf_exempt
def register(request):
    if request.method == 'POST':
       form = UserRegisterForm(request.POST)
       if form.is_valid():
            form.save()

            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username,password=password)

            # added this for error message
            if user :
                login(request,user)
                return redirect('home')
            else :
                messages.error(request,'There is something wrong with your input, please check through and get back to us!')
                return redirect ('contact')
       else:
            # print('Form not valid')
            messages.error(request,'There is lot wrong with your input, please check through and get back to us!')
            return redirect ('register')

    else:
        form = UserRegisterForm()
    context = {
       'form':form
    }
    return render (request, 'registration/register.html', context)

class Verify_Payment(APIView):
	def get(self, request):
		user = request.user
		# user_wallet = UserWallet.objects.get(user=user)
		# prev_amt = user_wallet.amount
		reference = request.GET.get("reference")
		url  = 'https://api.paystack.co/transaction/verify/'+reference
		headers = {
			"Authorization": "Bearer " + "sk_test_9559c105ee1b3354c2cd157b8140ea5d231ed77b"
			# "Authorization": "Bearer " + settings.PAYSTACK_SECRET_KEY
		}
		x = requests.get(url, headers=headers)
		if x.json()['status'] == False:
			return False
		results = x.json()
		if results['data']['status'] == 'success':
			amt= results["data"]["amount"]/100
			# user_wallet.prev_amount = prev_amt
			# user_wallet.save()
			PayHistory.objects.create(
				user=user, purpose="Purchase good",
				paystack_charge_id=results["data"]["reference"],
				amount=amt, paid=True, status=True
			)
		else:
			print('result is failed not success')
			# user_wallet.prev_amount = prev_amt
			# user_wallet.save()
			amt= results["data"]["amount"]/100
			PayHistory.objects.create(
				user=user, purpose="wallet",
				paystack_charge_id=results["data"]["reference"],
				amount=amt, paid=True, status=False
			)
		# current_wallet = UserWallet.objects.get(user=user)
		# current_wallet.amount += (results["data"]["amount"] /Decimal(100))
		# current_wallet.save()
		return Response(results)

