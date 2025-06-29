from django.shortcuts import render, redirect, HttpResponse
from datetime import datetime
import json

DEBIT_TYPES = ['asset', 'expense']
CREDIT_TYPES = ['liability', 'income', 'equity']


def home(request):
    try:
        with open('db.json', 'r') as file:
            db = json.load(file)
    except FileNotFoundError:
        db = {'accounts': {}, 'transactions': {}}
        db['transactions']['date'] = []
        db['transactions']['debit_account'] = []
        db['transactions']['credit_account'] = []
        db['transactions']['amount'] = []
        db['transactions']['describtion'] = []
        with open('db.json', 'w') as file:
            json.dump(db, file, indent=4)

    accounts = list(db["accounts"].keys())
    return render(request, "core/index.html", context={'accounts': accounts})


def add_account(request):
    if request.method == 'POST':
        with open('db.json', 'r') as file:
            db = json.load(file)

        account_name = request.POST.get('account_name')
        account_type = request.POST.get('account_type')

        if account_name not in db['accounts']:
            db['accounts'][account_name] = {
                'type': account_type, 'debit': [], 'credit': []}
        else:
            return HttpResponse('Account Already Exists')

        with open('db.json', 'w') as file:
            json.dump(db, file, indent=4)

    return redirect('/')
