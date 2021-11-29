from flask import render_template, redirect, url_for, flash, request
from flask.helpers import flash
import flask_login
from sqlalchemy.engine import url
from market.__init__ import app, db
from market.models import Item, User
from market.forms import RegisterForm, LoginForm, PurchaseItemForm, SellItemForm
from flask_login import login_user, logout_user, login_required, current_user

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/market', methods=['GET', 'POST'])
@login_required
def market():
    purchase_form = PurchaseItemForm()
    selling_form = SellItemForm()
    if request.method == 'POST':
        # Purchase Item Logic
        purchased_item =request.form.get('purchased_item')
        p_item_object = Item.query.filter_by(name=purchased_item).first()
        if p_item_object:
            if current_user.can_purchase(p_item_object):    
                p_item_object.buy(current_user)
                flash(f'Congratulations! You have purchased {p_item_object.name.capitalize()} for {p_item_object.price}$', category='success')
            else:
                flash(f'Unfortunately, you do not have enough money to purchase {p_item_object}', category='danger')
        # Sell Item Logic
        sold_item = request.form.get('sold_item')
        s_item_object = Item.query.filter_by(name=sold_item).first()
        if s_item_object:
            if current_user.can_sell(s_item_object):
                s_item_object.sell(current_user)
                flash(f'Congratulations! You sold {s_item_object.name} back to market! You recevied {s_item_object.price}$', category='success')
            else:
                flash(f'Something went wrong with selling {s_item_object.name}', category='danger')

        return redirect(url_for('market'))

    if request.method == 'GET':
        items = Item.query.filter_by(owner=None)
        owned_items = Item.query.filter_by(owner=current_user.id)
        return render_template('market.html', items = items, purchase_form=purchase_form, owned_items=owned_items, selling_form=selling_form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(
            username=form.username.data,
            email_address=form.email_address.data,
            password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()

        login_user(user_to_create)
        flash(f'Account created successfully! You are now logged in as: {user_to_create.username.capitalize()}', category='success')

        return redirect(url_for('market'))
    
    if form.errors != {}: # If there are no errors from the validations
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user {err_msg}', category='danger')

    return render_template('users/register.html',form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()

        if attempted_user and attempted_user.check_password_correction(attempted_password=form.password.data):
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.username.capitalize()}', category='success')
            return redirect(url_for('market'))

        else:
            flash('Username and password are not match! Please try again', category='danger')

    return render_template('users/login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash('You have logged out!', category='info')
    return redirect(url_for('home'))

@app.route('/about/<username>')
def about_page(username):
    return f'<h1>This is the about page of {username.capitalize()} </h1>'