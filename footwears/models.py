from django.db import models
from django.contrib.auth.models import User

# Create your models here.

# My category model
class Category(models.Model):
  categoryname = models.CharField(max_length=150)
  description = models.TextField()
  # categoryimage = models.CharField(max_length=150, default='default.jpg')
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
  # prodimage = models.CharField(max_length=150, default='default.jpg')
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
