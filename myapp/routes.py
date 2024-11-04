from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from . import db
from .models import User, Product
import os

main = Blueprint('main', __name__)
auth = Blueprint('auth', __name__)
admin = Blueprint('admin', __name__)

@main.route('/')
def home():
    products = Product.query.all()
    return render_template('home.html', products=products)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password) and user.is_admin:
            login_user(user)
            flash('Anda berhasil login.')
            return redirect(url_for('main.home'))
        flash('Username atau password salah')
    
    return render_template('admin/login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Anda berhasil logout.')
    return redirect(url_for('main.home'))

@admin.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_admin:
        flash("Anda tidak memiliki izin untuk mengakses halaman ini.")
        return redirect(url_for('main.home'))
    products = Product.query.all()
    return render_template('admin/dashboard.html', products=products)

@admin.route('/add-product', methods=['GET', 'POST'])
@login_required
def add_product():
    if not current_user.is_admin:
        return redirect(url_for('main.home'))
        
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        stock = int(request.form.get('stock'))
        
        # Handle image upload
        image = request.files.get('image')
        image_url = ''
        if image:
            filename = secure_filename(image.filename)
            image.save(os.path.join('static/img', filename))
            image_url = f'img/{filename}'
            
        product = Product(
            name=name,
            description=description,
            stock=stock,
            image_url=image_url
        )
        
        db.session.add(product)
        db.session.commit()
        flash('Produk Berhasil Ditambahkan.')
        return redirect(url_for('admin.dashboard'))
        
    return render_template('admin/add_product.html')

@admin.route('/delete-product/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    if not current_user.is_admin:
        flash("Anda tidak memiliki izin untuk menghapus barang.")
        return redirect(url_for('admin.dashboard'))
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Barang berhasil dihapus.')
    return redirect(url_for('admin.dashboard'))