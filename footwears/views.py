from django.core import mail
from footwears.context_processor import categories
from rest_framework import response
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
from django.conf import settings
from django.core.mail import send_mail

from django.http import response
from django.http.response import HttpResponseBadRequest, HttpResponseRedirectBase, JsonResponse
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
    if request.method=='POST':
        name =request.POST['name'] 
        email =request.POST['email'] 
        phone =request.POST['phone'] 
        subject =request.POST['subject'] 
        message =request.POST['message'] 

        save_message = Contact.objects.create(name=name, email=email, phone=phone, subject=subject, message=message)
        save_message.save()

        # send mail
        send_mail(
            subject,
            message,
            email,
            ['jelmah04@gmail.com'],
            fail_silently=True
        )
        # this message should be in a set interval/timeout function 
        messages.success(request, 'We have received your message, you will get a response shortly via your email.')
        return redirect('home')

    return render(request, 'footwears/contact.html')

def allfootwears(request,cat_id):
    # print(cat_id)
    products = Product.objects.filter(category__categoryname = cat_id)
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
                return redirect('login')
            else :
                messages.error(request,'There is something wrong with your input, please check through and get back to us!')
                return redirect ('contact')
       else:
            # print('Form not valid')
            messages.error(request,'Your form inputs are not valid, please check through and get back to us!')
            return redirect ('register')

    else:
        form = UserRegisterForm()
    context = {
       'form':form
    }
    return render (request, 'registration/register.html', context)


# The view function to create an order before payment and delete its detail from orderdetail
def order(request):
    print('About to make an order again')
    if request.is_ajax():
        amount = request.POST['amount']
        mycustomer=request.user.username
        ordercustomer = Customer.objects.get(user__username=request.user.username)
        current_address = ShippingAddress.objects.filter(customer=ordercustomer).first()  #just added for location
        ordernum = Orderdetail.objects.filter(user__username=mycustomer).first()
        fresh_order = Order.objects.create(order_number=ordernum.order_number, total_amount=amount, confirmation_status=False, delivery_status=False, customer=ordercustomer,location_to_ship_to =current_address.theaddress, location_call=current_address.themobiles)
        fresh_order.save()
        # delete order from orderdetails
        Orderdetail.objects.filter(order_placed=False).filter(user__username=request.user.username).delete()
    return redirect('init_payment')

# Initialise Payment with Paystack
def initialize(request):
	# if request.is_ajax():
    # I need to pass amount value from order function
    amount = 3000.00                          #request.POST['amount']
    email = request.user.email                #request.POST['email']
    # Call the endpoint here
    pay = init_payment(email,amount)

    if pay['status'] == False:
        msg = {"Error": "Error. Please try again."}
        print('The payment is not a success, so, am making a history')
        PayHistory.objects.create(
            user=request.user, 
            paystack_charge_id=pay["data"]["reference"],
            amount=pay["data"]["amount"],
            purpose="Purchase",
            status=False,
            paid=True, 
        )
        return JsonResponse(msg)
    else:
        msg = {"link": pay['data']['authorization_url']}
        print(msg)
        # Save Reference Code with product details to Database
        # pay['data']['reference']
        print('The payment is success, so, am making a history')
        PayHistory.objects.create(
            user=request.user, 
            paystack_charge_id=pay["data"]["reference"],
            # amount=pay["data"]["amount"] * 1.00,
            # amount=pay['data']['amount'] * 1.00,
            amount= 3000.00,
            purpose="Purchase",
            status=True,
            paid=True, 
        )
        # print('lets update our order model')
        ordercustomer = Customer.objects.get(user__username=request.user.username)
        Order.objects.filter(customer=ordercustomer).filter(confirmation_status=False).update(confirmation_status=True)
        # print('order model updated')
        return JsonResponse(msg)
    # return redirect('order')
        

def cart_view(request):
	allitems = Orderdetail.objects.filter(order_placed=False).filter(user__username=request.user.username).order_by('id').reverse()
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
    theprodid = request.POST['add_to_cart']
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
    shipaddrest = ShippingAddress.objects.filter(customer__user__username__iexact=request.user.username)

    total_amount = 0
    for x in items:
        total_amount += (x.product_unitprice * x.quantity)
    # total_amount = total_amount
    
    context = {
        'orderdetail':items,
        'customer_info':thecust,
        'totalamount':total_amount,
        # 'shippingaddress':shipaddress,
        'shippingaddrest':shipaddrest
    }
    return render(request,'footwears/checkout.html',context)


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
        collectnumber = request.POST['mobilenumber']
        collectaddress = request.POST['current_address']
        customer = Customer.objects.filter(user__username=request.user.username).first()
        if customer:
            newlocation = ShippingAddress.objects.create(theaddress=collectaddress, themobiles=collectnumber, customer=customer)
            newlocation.save()
        else:
            # print('This user does not have a customer profile, so lets create one')
            newcustomer = Customer.objects.create(mobiles=collectnumber, address=collectaddress, user=request.user)
            newcustomer.save()
            customer = Customer.objects.filter(user__username=request.user.username).first()
            newlocation = ShippingAddress.objects.create(theaddress=collectaddress, themobiles=collectnumber, customer=customer)
            newlocation.save()
    # print('addaddress')
    allitem = Orderdetail.objects.filter(order_placed=False).filter(user__username=request.user.username).first()
    pathe = allitem.order_number
    return redirect ( 'http://localhost/'+'checkout/'+ pathe)
    # return redirect('http://localhost/checkout/3587c89b-7cfb-4951-afc6-ca8e74daf8f9/')

def changeaddress(request):
    oldlocation = ShippingAddress.objects.filter(customer__user__username__iexact=request.user.username).delete()
    # print('changeaddress')
    allitem = Orderdetail.objects.filter(order_placed=False).filter(user__username=request.user.username).first()
    pathe = allitem.order_number
    return redirect ( 'http://localhost/'+'checkout/'+ pathe)
    # return redirect('http://localhost/checkout/3587c89b-7cfb-4951-afc6-ca8e74daf8f9/')
    ## An error that needed to be fixed
    ### [get() missing 1 required positional argument: 'header'] 


def search (request):
    find = Product.objects.all()

    if 'tosearch' in request.GET:
        tosearch = request.GET['tosearch']
        print(tosearch)
        if tosearch:
            find = find.filter(description__icontains=tosearch)
            print(find)
    context = {
        'find' : find,
    }
    return render(request, 'footwears/search.html', context)