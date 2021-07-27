from django.db import models
from django.contrib.auth.models import User

# Create your models here.

# My category model
class Category(models.Model):
  categoryname = models.CharField(max_length=150)
  description = models.TextField()
  categoryimage = models.ImageField(default='default.jpg')
  
  def __str__(self):
    return self.categoryname

  class Meta:
    db_table = 'categories'
    managed = True
    verbose_name = 'Category'
    verbose_name_plural = 'Categories'

# My Product model
class Product(models.Model):
  prodname = models.CharField(max_length=150)
  featured = models.BooleanField(default=False)
  prodimage = models.ImageField(default='default.jpg',null=True,blank=True)
  price = models.FloatField(null=True,blank=True)
  instock = models.BooleanField(default=True)
  quantity_instock = models.IntegerField(default=20)
  category = models.ForeignKey(Category,on_delete=models.CASCADE)

  def __str__(self):
    return self.prodname

  class Meta:
    db_table = 'products'
    managed = True
    verbose_name = 'Product'
    verbose_name_plural = 'Products'



# Payment Gateway
# Pay History
class PayHistory(models.Model):
	pur = (
		("shoes", "shoe"),
		("headwear", "headwear"),
		("other", "Other")
	)
	user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
	paystack_charge_id = models.CharField(max_length=100, default='', blank=True)
	paystack_access_code = models.CharField(max_length=100, default='', blank=True)
	amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
	purpose = models.CharField(max_length=100, default='Product', choices=pur)
	status = models.CharField(max_length=100, default='')
	paid = models.BooleanField(default=False)
	date = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.user.username


# orderdetail # cart and container for order details
class Orderdetail(models.Model):
  product = models.ForeignKey(Product,on_delete=models.DO_NOTHING,null=True,blank=True)
  product_image = models.ImageField(default='default.jpg',null=True,blank=True)
  order_number = models.CharField(max_length=70)
  product_name = models.CharField(max_length=50)
  product_unitprice = models.FloatField(null=True,blank=True)
  quantity = models.IntegerField(default=1)
  user = models.ForeignKey(User,on_delete=models.CASCADE)
  order_placed = models.BooleanField(default=False)
  date = models.DateTimeField(auto_now_add=True)


  def __str__(self):
    return f'{self.user.username} ============> {self.product_name} ===========> {self.order_number}'

  class Meta:
    db_table = 'orderdetails'
    managed = True
    verbose_name = 'Orderdetail'
    verbose_name_plural = 'Orderdetails'


# customer # user profile
class Customer(models.Model):
  mobiles = models.CharField(max_length=150, null=True, blank=False, default='08111111111')
  address = models.TextField(max_length=450, null=True, blank=False, default='nigeria')
  user = models.ForeignKey(User,on_delete=models.DO_NOTHING)

  def __str__(self):
    return self.user.username

  class Meta:
    db_table = 'customers'
    managed = True
    verbose_name = 'Customer'
    verbose_name_plural = 'Customers'


# Shipping Address
class ShippingAddress(models.Model):
  theaddress = models.TextField(max_length=450)
  themobiles = models.CharField(max_length=150, null=True, blank=False, default='08111111111')
  mycurrent = models.BooleanField(default=False)
  customer = models.ForeignKey(Customer,on_delete=models.CASCADE)

  def __str__(self):
    return self.theaddress

  class Meta:
    db_table = 'shippingaddresses'
    managed = True
    verbose_name = 'ShippingAddress'
    verbose_name_plural = 'ShippingAddresss'


# order
class Order(models.Model):
  order_number = models.CharField(max_length=70)
  total_amount = models.FloatField()
  confirmation_status = models.BooleanField(default=False)
  delivery_status = models.BooleanField(default=False)
  customer = models.ForeignKey(Customer,on_delete=models.DO_NOTHING)
  location_to_ship_to = models.CharField(max_length=2000, default='number 1, Imise road, Onihale, Ifo, Oyostate')

  def __str__(self):
    return self.customer.user.username

  class Meta:
    db_table = 'orders'
    managed = True
    verbose_name = 'Order'
    verbose_name_plural = 'Orders'


class Wishlist(models.Model):
  product = models.ForeignKey(Product,on_delete=models.CASCADE)
  customer = models.ForeignKey(Customer,on_delete = models.CASCADE)
  date_created = models.DateTimeField(auto_now_add=True,null=True,blank=True)
  now_bought = models.BooleanField(default=False)
  user = models.ForeignKey(User,on_delete = models.CASCADE)

  def __str__(self):
    return self.user.username

  class Meta:
    db_table = 'wishlists'
    managed = True
    verbose_name = 'Wishlist'
    verbose_name_plural = 'Wishlists'
