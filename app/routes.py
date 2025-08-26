# app/routes.py
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from app import app, db
from app.forms import LoginForm, RegistrationForm, AnnouncementForm, CategoryForm, QuestionForm, AnswerForm
from app.models import User, Announcement, Category, Question, Purchase
from datetime import datetime

@app.route('/')
@app.route('/index')
def index():
    announcements = Announcement.query.filter_by(purchase=None).order_by(Announcement.timestamp.desc()).all()
    return render_template('index.html', title='Página Principal', announcements=announcements)

# --- Rotas de Autenticação ---
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

# --- Rotas do Utilizador ---
@app.route('/meus_anuncios')
@login_required
def my_announcements():
    announcements = current_user.announcements.order_by(Announcement.timestamp.desc()).all()
    return render_template('my_announcements.html', announcements=announcements)

@app.route('/minhas_compras')
@login_required
def my_purchases():
    purchases = current_user.purchases.order_by(Purchase.timestamp.desc()).all()
    return render_template('my_purchases.html', purchases=purchases)

@app.route('/minhas_vendas')
@login_required
def my_sales():
    sales = Purchase.query.join(Announcement).filter(Announcement.user_id == current_user.id).order_by(Purchase.timestamp.desc()).all()
    return render_template('my_sales.html', sales=sales)

@app.route('/meus_favoritos')
@login_required
def my_favorites():
    favorites = current_user.favorited.order_by(Announcement.timestamp.desc()).all()
    return render_template('my_favorites.html', favorites=favorites)

# --- CRUD de Anúncios ---
@app.route('/anuncio/novo', methods=['GET', 'POST'])
@login_required
def new_announcement():
    form = AnnouncementForm()
    form.category_id.choices = [(c.id, c.name) for c in Category.query.order_by('name').all()]
    if form.validate_on_submit():
        announcement = Announcement(
            title=form.title.data, 
            description=form.description.data, 
            price=form.price.data, 
            author=current_user,
            category_id=form.category_id.data
        )
        db.session.add(announcement)
        db.session.commit()
        flash('Anúncio publicado com sucesso!', 'success')
        return redirect(url_for('index'))
    return render_template('announcement_form.html', title='Novo Anúncio', form=form)

@app.route('/anuncio/<int:id>')
def announcement_detail(id):
    announcement = Announcement.query.get_or_404(id)
    question_form = QuestionForm()
    answer_form = AnswerForm()
    return render_template('announcement_detail.html', announcement=announcement, question_form=question_form, answer_form=answer_form)

@app.route('/anuncio/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_announcement(id):
    announcement = Announcement.query.get_or_404(id)
    if current_user != announcement.author:
        flash('Você não tem permissão para editar este anúncio.', 'danger')
        return redirect(url_for('index'))
    form = AnnouncementForm(obj=announcement)
    form.category_id.choices = [(c.id, c.name) for c in Category.query.order_by('name').all()]
    if form.validate_on_submit():
        announcement.title = form.title.data
        announcement.description = form.description.data
        announcement.price = form.price.data
        announcement.category_id = form.category_id.data
        db.session.commit()
        flash('Anúncio atualizado com sucesso!', 'success')
        return redirect(url_for('announcement_detail', id=announcement.id))
    return render_template('announcement_form.html', title='Editar Anúncio', form=form)

@app.route('/anuncio/deletar/<int:id>', methods=['POST'])
@login_required
def delete_announcement(id):
    announcement = Announcement.query.get_or_404(id)
    if current_user != announcement.author:
        flash('Você não tem permissão para excluir este anúncio.', 'danger')
        return redirect(url_for('index'))
    db.session.delete(announcement)
    db.session.commit()
    flash('Anúncio excluído com sucesso!', 'danger')
    return redirect(url_for('index'))

# --- Rotas de Categorias ---
@app.route('/categorias')
def list_categories():
    categories = Category.query.order_by('name').all()
    return render_template('categories.html', categories=categories)

@app.route('/categoria/nova', methods=['GET', 'POST'])
@login_required
def new_category():
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(name=form.name.data)
        db.session.add(category)
        db.session.commit()
        flash('Categoria criada com sucesso!', 'success')
        return redirect(url_for('list_categories'))
    return render_template('category_form.html', form=form, title='Nova Categoria')

# --- Funcionalidades (Perguntas, Compras, Favoritos) ---
@app.route('/anuncio/<int:id>/perguntar', methods=['POST'])
@login_required
def ask_question(id):
    announcement = Announcement.query.get_or_404(id)
    form = QuestionForm()
    if form.validate_on_submit():
        question = Question(body=form.body.data, asker=current_user, announcement=announcement)
        db.session.add(question)
        db.session.commit()
        flash('A sua pergunta foi enviada.', 'success')
    return redirect(url_for('announcement_detail', id=id))

@app.route('/pergunta/<int:id>/responder', methods=['POST'])
@login_required
def answer_question(id):
    question = Question.query.get_or_404(id)
    if current_user != question.announcement.author:
        flash('Você não pode responder a esta pergunta.', 'danger')
        return redirect(url_for('announcement_detail', id=question.announcement_id))
    form = AnswerForm()
    if form.validate_on_submit():
        question.answer = form.answer.data
        question.answer_timestamp = datetime.utcnow()
        db.session.commit()
        flash('A sua resposta foi enviada.', 'success')
    return redirect(url_for('announcement_detail', id=question.announcement_id))

@app.route('/anuncio/<int:id>/comprar', methods=['POST'])
@login_required
def buy_announcement(id):
    announcement = Announcement.query.get_or_404(id)
    if announcement.author == current_user:
        flash('Você não pode comprar o seu próprio anúncio.', 'warning')
        return redirect(url_for('announcement_detail', id=id))
    if announcement.purchase:
        flash('Este anúncio já foi vendido.', 'danger')
        return redirect(url_for('announcement_detail', id=id))
    
    purchase = Purchase(buyer=current_user, announcement=announcement)
    db.session.add(purchase)
    db.session.commit()
    flash('Parabéns pela sua compra!', 'success')
    return redirect(url_for('my_purchases'))

@app.route('/favoritar/<int:id>')
@login_required
def add_favorite(id):
    announcement = Announcement.query.get_or_404(id)
    current_user.add_favorite(announcement)
    db.session.commit()
    flash('Anúncio adicionado aos favoritos!', 'success')
    return redirect(request.referrer or url_for('index'))

@app.route('/desfavoritar/<int:id>')
@login_required
def remove_favorite(id):
    announcement = Announcement.query.get_or_404(id)
    current_user.remove_favorite(announcement)
    db.session.commit()
    flash('Anúncio removido dos favoritos.', 'info')
    return redirect(request.referrer or url_for('index'))
