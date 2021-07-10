from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('contact', views.contact, name='contact'),
    path('allfootwears', views.allfootwears, name='allfootwears'),
    path('allheadwears', views.allheadwears, name='allheadwears'),
    path('single/<str:prod_id>/', views.single, name='single'),
    path('register/',views.register,name='register'),
    path('webhook/',views.webhook,name='webhook'),
    path('verify_transaction/',views.Verify_Payment,name='verify_transaction'),
]