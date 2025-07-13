from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('add_account', views.add_account, name='add_account'),
    path('add_transaction', views.add_transaction, name='add_transaction'),
    path('transactions', views.transactions_report, name='transactions_report'),
    path('accounts_balance', views.accounts_balance, name='accounts_balance'),
    path('persons_report', views.persons_report, name='persons_report'),
    path('income_expense_report', views.income_expense_report, name='income_expense_report'),
    path('balance-sheet', views.balance_sheet, name='balance_sheet'),
    path('transactions/delete/<str:txn_id>/', views.delete_transaction, name='delete_transaction'),
]
