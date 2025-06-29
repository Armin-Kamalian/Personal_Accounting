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

        account_name = request.POST.get('account_name').strip().title()
        account_type = request.POST.get('account_type')

        if account_name not in db['accounts']:
            db['accounts'][account_name] = {
                'type': account_type, 'debit': [], 'credit': []}
        else:
            return HttpResponse('Account Already Exists')

        with open('db.json', 'w') as file:
            json.dump(db, file, indent=4)

    return redirect('/')


def add_transaction(request):
    if request.method == 'POST':
        with open('db.json', 'r') as file:
            db = json.load(file)

        debit_account = request.POST.get('debit_account')
        credit_account = request.POST.get('credit_account')
        describtion = request.POST.get('describtion')
        date = request.POST.get('date')

        if debit_account not in db['accounts'] or credit_account not in db['accounts']:
            return HttpResponse("One of the accounts does not exist!", status=400)

        try:
            amount = int(request.POST.get('amount'))
        except (ValueError, TypeError):
            return HttpResponse("Invalid amount", status=400)

        db['accounts'][debit_account]['debit'].append(amount)
        db['accounts'][credit_account]['credit'].append(amount)

        db['transactions']['date'].append(date)
        db['transactions']['debit_account'].append(debit_account)
        db['transactions']['credit_account'].append(credit_account)
        db['transactions']['amount'].append(amount)
        db['transactions']['describtion'].append(describtion)

        with open('db.json', 'w') as file:
            json.dump(db, file, indent=4)

        return redirect('/')
