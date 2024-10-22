from flask import Flask, render_template, request, redirect, url_for, jsonify
import json

app = Flask(__name__)

users = {}
expenses = []
user_id = 1
user_balances = {}


@app.route('/add', methods=['GET', 'POST'])
def add_user():
    global user_id
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        mobile = request.form['mobile']
        users[user_id] = {'name': name, 'email': email, 'mobile': mobile}
        user_id += 1
        return redirect(url_for('list_users'))
    return render_template('add.html')


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
    user = users.get(id)
    if request.method == 'POST':
        users[id]['name'] = request.form['name']
        users[id]['email'] = request.form['email']
        users[id]['mobile'] = request.form['mobile']
        return redirect(url_for('list_users'))
    return render_template('edit.html', user=user)


@app.route('/delete/<int:id>')
def delete_user(id):
    if id in users:
        del users[id]
    return redirect(url_for('list_users'))

# List users route
@app.route('/users')
def list_users():
    return render_template('users.html', users=users)
# Add expense route
@app.route('/add_expense', methods=['GET', 'POST'])
def add_expense():
    if request.method == 'POST':
        description = request.form['description']
        amount = float(request.form['amount'])
        participants = request.form.getlist('participants')
        payer = request.form['payer']  
        split_method = request.form['split_method']
        print(f'Description: {description}, Amount: {amount}, Participants: {participants}, Payer: {payer}, Split Method: {split_method}')

        splits = {}
        if split_method == 'equal':
            per_person = amount / len(participants)
            splits = {user: per_person for user in participants}

        elif split_method == 'exact':
            splits = {user: float(request.form[f'exact_amount_{user}']) for user in participants}

        elif split_method == 'percentage':
            splits = {user: (amount * float(request.form[f'percentage_{user}']) / 100) for user in participants}

        expenses.append({
            'description': description,
            'amount': amount,
            'payer': payer, 
            'splits': splits
        })
        print(expenses)
        return redirect(url_for('list_expenses'))

    return render_template('add_expense.html', users=users)


@app.route('/expenses')
def list_expenses():
    return render_template('expenses.html', expenses=expenses, users=users)

@app.route('/balance_sheet')
def balance_sheet():
    global user_balances
    user_balances = {user: 0.0 for user in users} 
    
    for expense in expenses:
        payer = int(expense['payer'])
        amount = expense['amount']
        
        user_balances[payer] += amount
        
        for user, owed_amount in expense['splits'].items():
            user_balances[int(user)] -= owed_amount
    
    return render_template('balance_sheet.html', user_balances=user_balances, users=users)

@app.route('/download_balance_sheet')
def download_balance_sheet():
    balance_data = {'balances': {users[user]['name']: balance for user, balance in user_balances.items()}}
    response = app.response_class(
        response=json.dumps(balance_data, indent=2),
        mimetype='application/json'
    )
    response.headers['Content-Disposition'] = 'attachment; filename=balance_sheet.json'
    return response


if __name__ == '__main__':
    app.run(debug=True)
