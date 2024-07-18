from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
from forms import RegistrationForm, LoginForm, UpdateAccountForm, ProductForm
from utils import generate_bitcoin_address, get_bitcoin_balance
import qrcode
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

from models import User, Product

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@app.route('/home')
def home():
    products = Product.query.all()
    return render_template('home.html', products=products)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        bitcoin_address = generate_bitcoin_address()
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, bitcoin_address=bitcoin_address)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    bitcoin_balance_eur, bitcoin_balance_btc = get_bitcoin_balance(current_user.bitcoin_address)
    return render_template('profile.html', title='Profile', form=form, bitcoin_balance_eur=bitcoin_balance_eur, bitcoin_balance_btc=bitcoin_balance_btc)

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if not current_user.is_admin:
        return redirect(url_for('home'))
    form = AdminLoginForm()
    if form.validate_on_submit():
        if form.password.data == '113802009Alpha*!':
            return redirect(url_for('admin_home'))
        else:
            flash('Invalid admin password', 'danger')
            return redirect(url_for('home'))
    return render_template('admin/admin_login.html', title='Admin Login', form=form)

@app.route('/admin/home')
@login_required
def admin_home():
    if not current_user.is_admin:
        return redirect(url_for('home'))
    products = Product.query.all()
    return render_template('admin/admin_home.html', products=products)

@app.route('/admin/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    if not current_user.is_admin:
        return redirect(url_for('home'))
    form = ProductForm()
    if form.validate_on_submit():
        product = Product(title=form.title.data, description=form.description.data, price=form.price.data, image_file=form.picture.data.filename)
        db.session.add(product)
        db.session.commit()
        flash('Product has been added!', 'success')
        return redirect(url_for('admin_home'))
    return render_template('admin/add_product.html', title='Add Product', form=form)

@app.route('/admin/delete_product', methods=['GET', 'POST'])
@login_required
def delete_product():
    if not current_user.is_admin:
        return redirect(url_for('home'))
    products = Product.query.all()
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        product = Product.query.get(product_id)
        db.session.delete(product)
        db.session.commit()
        flash('Product has been deleted!', 'success')
        return redirect(url_for('admin_home'))
    return render_template('admin/delete_product.html', title='Delete Product', products=products)

if __name__ == '__main__':
    app.run(debug=True)