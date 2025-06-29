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
