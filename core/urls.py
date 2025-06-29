from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('add_account', views.add_account, name='add_account'),
    path('add_transaction', views.add_account, name='add_transaction'),
]
