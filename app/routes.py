# Contém a lógica para cada página (rota) da sua aplicação.

from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_user, logout_user, login_required
from app import app, db
from app.forms import LoginForm, RegistrationForm, ProductForm
from app.models import User, Product

@app.route('/')
@app.route('/index')
@login_required
def index():
    products = Product.query.all()
    return render_template('index.html', title='Início', products=products)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Nome de utilizador ou senha inválidos', 'danger')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Entrar', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Parabéns, o seu registo foi efetuado com sucesso!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Registar', form=form)

# --- CRUD de Produtos ---

@app.route('/product/new', methods=['GET', 'POST'])
@login_required
def new_product():
    form = ProductForm()
    if form.validate_on_submit():
        product = Product(name=form.name.data, description=form.description.data, price=form.price.data)
        db.session.add(product)
        db.session.commit()
        flash('Produto adicionado com sucesso!', 'success')
        return redirect(url_for('index'))
    return render_template('product_form.html', title='Novo Produto', form=form)

@app.route('/product/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    product = Product.query.get_or_404(id)
    form = ProductForm(obj=product)
    if form.validate_on_submit():
        product.name = form.name.data
        product.description = form.description.data
        product.price = form.price.data
        db.session.commit()
        flash('Produto atualizado com sucesso!', 'success')
        return redirect(url_for('index'))
    return render_template('product_form.html', title='Editar Produto', form=form)

@app.route('/product/delete/<int:id>', methods=['POST'])
@login_required
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash('Produto excluído com sucesso!', 'danger')
    return redirect(url_for('index'))
