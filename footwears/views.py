from footwears.context_processor import categories
from rest_framework import response
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
from django.conf import settings

from django.http import response
from django.http.response import JsonResponse
from django.http import HttpResponseRedirect
from .payment import init_payment
from django.shortcuts import render
import secrets
import uuid
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
    # print(cat_id)
    products = Product.objects.all()
    context = {
        'products' : products
    }
    return render(request, 'footwears/allfootwears.html', context)

@login_required
def single(request, prod_id):
    single = Product.objects.get(pk=prod_id)
    context = {
        'single' : single
    }
    return render(request, 'footwears/single.html', context)

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


# Initialise Payment with Paystack
def initialize(request):
	if request.is_ajax():
		amount = request.POST['amount']
		email = request.POST['email']
		# Call the endpoint here
		pay = init_payment(email,amount)

		if pay['status'] == False:
			msg = {"Error": "Error. Please try again."}
			return JsonResponse(msg)
		else:
			msg = {"link": pay['data']['authorization_url']}
			# Save Reference Code with product details to Database
			# pay['data']['reference']
			return JsonResponse(msg)
        # Order.objects.create()
        

def cart_view(request):
	allitems = Orderdetail.objects.filter(order_placed=False).filter(user__username=request.user.username)
	total_amount = 0

	for item in allitems:
		total_amount +=(item.product_unitprice * item.quantity)

	context = {
        'allitems':allitems,
        'totalamount':total_amount
    }
	return render (request, 'footwears/cart.html', context)


@login_required(login_url='login')
def updatequantity(request):
    if request.method == 'POST':
        newquantity = request.POST['itemquantity']
        theitem = Orderdetail.objects.get(id=request.POST['itemid'])
        if int(newquantity) > 0 :
            theitem.quantity = newquantity
            theitem.save()
        else:
            print('something is wrong')
    return redirect('cart')


@login_required(login_url='login')
def removefromcart(request):
    Orderdetail.objects.get(id=request.POST['deleteTarget']).delete()
    return redirect('cart')


@login_required(login_url='login')
def addtocart(request):
  # theproduct = Product.objects.get(pk=prod_id)
  if request.method == 'POST':
    theprodid = request.POST['tayo']
    aprod = Product.objects.get(pk=theprodid)
    #check if the user has an existing cart
    cart = Orderdetail.objects.filter(order_placed=False).filter(user__username = request.user.username)

    if cart:
        print('got a basket')
        # check if the product is already in the cart
        prodchecker = Orderdetail.objects.filter(product__id = aprod.id).filter(user__username = request.user.username).first()
        if prodchecker:
            # print('yes prod is in it')
            prodchecker.quantity += 1
            prodchecker.save()
            return redirect('home')
        else:
            # print(' No prod in it so You can now add into it')
            Orderdetail.objects.create(product=aprod,user=request.user,order_number=cart[0].order_number,product_name=aprod.prodname,product_unitprice=aprod.price,quantity=1,product_image=aprod.prodimage, order_placed=False)
            return redirect('home')
    else:
        # print('has no basket')
        ## create cart and add product to it
        orderID = str(uuid.uuid4())
        nucart = Orderdetail.objects.create(product=aprod,product_image=aprod.prodimage,user=request.user,order_number=orderID,product_name=aprod.prodname,product_unitprice=aprod.price,quantity=1,order_placed=False)
        print('No basket. New OrderID:',orderID)
    return redirect('home')
  #create a shopping cart => with UUID


@login_required(login_url='login')
def checkout(request,q):
    items = Orderdetail.objects.filter(order_number__iexact=q).filter(user__username__iexact=request.user.username)
    thecust = Customer.objects.filter(user__username__iexact=request.user.username).first()
    # shipaddress = ShippingAddress.objects.filter(mycurrent__exact=True).filter(customer__user__username__iexact=request.user.username).first()
    shipaddrest = ShippingAddress.objects.all().filter(customer__user__username__iexact=request.user.username)

    total_amount = 0
    for x in items:
        total_amount += (x.product_unitprice * x.quantity)
    
    context = {
        'orderdetail':items,
        'customer_info':thecust,
        'totalamount':total_amount,
        # 'shippingaddress':shipaddress,
        'shippingaddrest':shipaddrest
    }
    return render(request,'footwears/checkout.html',context)


class Verify_Payment(APIView):
	def get(self, request):
		user = request.user
		reference = request.GET.get("reference")
		url = 'https://api.paystack.co/transaction/verify/'+reference
		headers = {
			"Authorization": "Bearer " +settings.PAYSTACK_SECRET_KEY
		}
		x = requests.get(url, headers=headers)
		if x.json()['status'] == False:
			return False
		results = x.json()
		if results['data']['status'] == 'success':
			Order.objects.create(
				customer=user, 
				order_number=results["data"]["reference"],
				total_amount=results["data"]["amount"], 
                confirmation_status=True,
                delivery_status=False
			)
		else:
			Order.objects.create(
				customer=user, 
				order_number=results["data"]["reference"],
				total_amount=results["data"]["amount"], 
                confirmation_status=False,
                delivery_status=False
			)

		return Response(results)


# def webhook (request):
# 	if request.method == 'POST':
# 		email = request.POST['email']
# 		amount = request.POST['prodamount']
# 		username = request.user.username
# 		lastname = request.user.last_name
# 		amount = int(amount)*100

# 		# print(email)print(username)print(lastname)print(amount)
# 		initialized = init_payment(username, lastname, email, amount)
# 		print(initialized["data"]["authorization_url"])
# 		amount = amount/100
# 		instance = PayHistory.objects.create(amount=amount, user=request.user, paystack_charge_id=initialized['data']['reference'], paystack_access_code=initialized['data']['access_code'])

# 		# wallet = UserWallet.objects.get(user=request.user)
# 		# old_amt = wallet + amount
# 		# wallet.save()
		
# 		link = initialized['data']['authorization_url']
# 		return HttpResponseRedirect(link)
# 	return render (request, 'webhook.html')

@login_required(login_url='login')
def wishlist(request):
  thelist = Wishlist.objects.filter(customer__user__username__iexact=request.user.username).filter(now_bought__exact=False)
  context = {
    'wishlist':thelist
  }
  return render(request,'footwears/wishlist.html',context)

@login_required(login_url='login')
def dewishlist(request):
  if request.method == 'POST':
    Wishlist.objects.get(id=request.POST['deleteWishTarget']).delete()

  return redirect('wishlist')


def wishpage_func(request):
    if request.method == 'POST':
        wishproductid = request.POST['wishitem']
        wishprod = Product.objects.get(pk=wishproductid)
        custo = Customer.objects.get(user=request.user)
        newwish = Wishlist.objects.create(product=wishprod, customer=custo, now_bought=False, user=request.user)
        newwish.save()
    else:
        print('This is difficult to fix')
    return redirect('home')


def addaddress(request):
    if request.method == 'POST':
        collect = request.POST['location']
        customer = Customer.objects.get(user=request.user)
        newlocation = ShippingAddress.objects.create(theaddress=collect, mycurrent=False, customer=customer)
        newlocation.save()
    # return HttpResponseRedirect
    # return redirect('checkout')
