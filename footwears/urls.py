from django.urls import path
from django.conf.urls import url
from . import views
# from .views import initialize, init_payment
urlpatterns = [
    path('', views.home, name='home'),
    path('contact/', views.contact, name='contact'),
    path('allfootwears/<str:cat_id>/', views.allfootwears, name='allfootwears'),
    path('single/<str:prod_id>/', views.single, name='single'),
    path('register/',views.register,name='register'),
    path('cart_page/',views.cart_view,name='cart'),
    path('removefromcart/',views.removefromcart,name='removefromcart'),
    path('updatequantity/',views.updatequantity,name='updatequantity'),
    path('addtocart/', views.addtocart, name='addtocart'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishpage_func/', views.wishpage_func, name='wishpage_func'),
    path('dewishlist/', views.dewishlist, name='dewishlist'),
    path('checkout/<str:q>/', views.checkout, name='checkout'),
    path('addaddress/', views.addaddress, name='addaddress'),
    path('changeaddress/', views.changeaddress, name='changeaddress'),
    path('order/', views.order, name='order'),
    path('search/', views.search, name='search'),
    url(r'initialize_payment/$', views.initialize, name='init_payment'),
]