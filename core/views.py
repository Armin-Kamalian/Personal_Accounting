from django.shortcuts import render, redirect, HttpResponse
from datetime import datetime
import json
import uuid


FILE_NAME = 'db.json'
ACCOUNT_TYPES = ['asset', 'liability', 'income', 'expense', 'equity', 'person']
DEBIT_TYPES = ['asset', 'expense', 'person']
CREDIT_TYPES = ['liability', 'income', 'equity']


def home(request):
    try:
        with open(FILE_NAME, 'r', encoding='utf-8') as file:
            db = json.load(file)
    except FileNotFoundError:
        db = {'accounts': {}, 'transactions': {}}
        with open(FILE_NAME, 'w', encoding='utf-8') as file:
            json.dump(db, file, indent=4, ensure_ascii=False)

    accounts = sorted(db['accounts'].keys())
    return render(request, 'core/index.html', context={'accounts': accounts})


def add_account(request):
    if request.method == 'POST':
        with open(FILE_NAME, 'r', encoding='utf-8') as file:
            db = json.load(file)

        account_name = request.POST.get('account_name').strip().title()
        account_type = request.POST.get('account_type')

        if account_name not in db['accounts']:
            db['accounts'][account_name] = {
                'type': account_type, 'debit': [], 'credit': []}
        else:
            return HttpResponse('Account Already Exists')

        with open(FILE_NAME, 'w', encoding='utf-8') as file:
            json.dump(db, file, indent=4, ensure_ascii=False)

    return redirect('/')


def add_transaction(request):
    if request.method == 'POST':
        with open(FILE_NAME, 'r', encoding='utf-8') as file:
            db = json.load(file)

        debit_account = request.POST.get('debit_account')
        credit_account = request.POST.get('credit_account')
        description = request.POST.get('description')
        date = request.POST.get('date')

        if debit_account not in db['accounts'] or credit_account not in db['accounts']:
            return HttpResponse('One of the accounts does not exist!', status=400)

        try:
            amount = int(request.POST.get('amount'))
        except (ValueError, TypeError):
            return HttpResponse('Invalid amount', status=400)

        db['accounts'][debit_account]['debit'].append(amount)
        db['accounts'][credit_account]['credit'].append(amount)

        transaction_id = str(uuid.uuid4())
        db['transactions'][transaction_id] = {
            'date': date,
            'debit_account': debit_account,
            'credit_account': credit_account,
            'amount': amount,
            'description': description
        }

        with open(FILE_NAME, 'w', encoding='utf-8') as file:
            json.dump(db, file, indent=4, ensure_ascii=False)

        return redirect('/')


def transactions_report(request):
    with open(FILE_NAME, 'r', encoding='utf-8') as file:
        db = json.load(file)

    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    transactions = []

    for txn_id, txn in db['transactions'].items():
        try:
            date_obj = datetime.strptime(txn['date'], '%Y-%m-%d').date()
        except Exception:
            continue

        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            if date_obj < start_date:
                continue

        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            if date_obj > end_date:
                continue

        transaction = txn.copy()
        transaction['id'] = txn_id
        transactions.append(transaction)
        transactions.sort(key=lambda x: x['date'])

    context = {
        'transactions': transactions,
        'start_date': start_date_str,
        'end_date': end_date_str,
    }
    return render(request, 'core/transactions_list.html', context)


def accounts_balance(request):
    selected_types = request.GET.getlist('type')

    with open(FILE_NAME, 'r', encoding='utf-8') as file:
        db = json.load(file)

    balances = []

    for account_name, info in db['accounts'].items():
        acc_type = info.get('type')

        if selected_types and acc_type not in selected_types:
            continue

        debit_total = sum(info.get('debit', []))
        credit_total = sum(info.get('credit', []))

        if acc_type in DEBIT_TYPES:
            balance = debit_total - credit_total
        elif acc_type in CREDIT_TYPES:
            balance = credit_total - debit_total
        else:
            balance = 0

        balances.append({
            'name': account_name,
            'type': acc_type,
            'debit_total': debit_total,
            'credit_total': credit_total,
            'balance': balance
        })

        balances.sort(key=lambda x: (x['type'], -x['balance']))

    return render(request, 'core/accounts_balance.html', {
        'balances': balances,
        'selected_types': selected_types,
        'account_types': ACCOUNT_TYPES
    })


def persons_report(request):
    with open(FILE_NAME, 'r', encoding='utf-8') as file:
        db = json.load(file)

    persons = []

    for name, info in db['accounts'].items():
        if info['type'] == 'person':
            debit_total = sum(info.get('debit', []))
            credit_total = sum(info.get('credit', []))
            balance = debit_total - credit_total

            status = 'Debtor' if balance > 0 else 'Creditor' if balance < 0 else 'Settled'

            persons.append({
                'name': name,
                'debit_total': debit_total,
                'credit_total': credit_total,
                'balance': abs(balance),
                'status': status
            })

    return render(request, 'core/persons_report.html', {'persons': persons})


def income_expense_report(request):

    with open(FILE_NAME, 'r', encoding='utf-8') as file:
        db = json.load(file)

    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    income_total = 0
    expense_total = 0

    income_transactions = []
    expense_transactions = []

    for txn_id, txn in db['transactions'].items():
        try:
            date_obj = datetime.strptime(txn['date'], '%Y-%m-%d').date()
        except Exception:
            continue

        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            if date_obj < start_date:
                continue

        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            if date_obj > end_date:
                continue

        if db['accounts'][txn['debit_account']]['type'] == 'expense':
            expense_total += txn['amount']
            expense_transactions.append(txn)

        if db['accounts'][txn['credit_account']]['type'] == 'income':
            income_total += txn['amount']
            income_transactions.append(txn)

    NET_RESULT = income_total - expense_total
    context = {
        'income_total': income_total,
        'expense_total': expense_total,
        'income_transactions': income_transactions,
        'expense_transactions': expense_transactions,
        'start_date': start_date_str,
        'end_date': end_date_str,
        'net_result': NET_RESULT,
    }
    return render(request, 'core/income_expense.html', context)


def balance_sheet(request):
    with open(FILE_NAME, 'r', encoding='utf-8') as file:
        db = json.load(file)

    assets = []
    liabilities = []
    equities = []

    total_assets = total_liabilities = total_equity = 0

    for name, info in db['accounts'].items():
        debit_total = sum(info.get('debit', []))
        credit_total = sum(info.get('credit', []))
        acc_type = info['type']

        if acc_type == 'asset':
            balance = debit_total - credit_total
            assets.append({'name': name, 'balance': balance})
            total_assets += balance

        elif acc_type in ['liability']:
            balance = credit_total - debit_total
            liabilities.append({'name': name, 'balance': balance})
            total_liabilities += balance

        elif acc_type in ['person']:
            balance = credit_total - debit_total
            liabilities.append({'name': name, 'balance': balance})
            total_liabilities += balance

        elif acc_type == 'equity':
            balance = credit_total - debit_total
            equities.append({'name': name, 'balance': balance})
            total_equity += balance

        YOU_HAVE = total_assets - total_liabilities

    return render(request, 'core/balance_sheet.html', {
        'assets': assets,
        'liabilities': liabilities,
        'equities': equities,
        'total_assets': total_assets,
        'total_liabilities': total_liabilities,
        'total_equity': total_equity,
        'you_have': YOU_HAVE,
    })


def delete_transaction(request, txn_id):
    with open(FILE_NAME, 'r', encoding='utf-8') as file:
        db = json.load(file)

    if txn_id in db['transactions']:
        txn = db['transactions'][txn_id]

        debit_account = txn['debit_account']
        credit_account = txn['credit_account']
        amount = txn['amount']

        if amount in db['accounts'][debit_account]['debit']:
            db['accounts'][debit_account]['debit'].remove(amount)

        if amount in db['accounts'][credit_account]['credit']:
            db['accounts'][credit_account]['credit'].remove(amount)

        del db['transactions'][txn_id]

        with open(FILE_NAME, 'w', encoding='utf-8') as file:
            json.dump(db, file, indent=4, ensure_ascii=False)

        return redirect('/transactions')
    else:
        return HttpResponse('Transaction not found', status=404)
