# app/models.py
from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

# Tabela de associação para favoritos (relação muitos-para-muitos)
favorites = db.Table('favorites',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('announcement_id', db.Integer, db.ForeignKey('announcement.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(256))
    
    # Relações
    announcements = db.relationship('Announcement', backref='author', lazy='dynamic', foreign_keys='Announcement.user_id')
    questions_asked = db.relationship('Question', backref='asker', lazy='dynamic', foreign_keys='Question.user_id')
    purchases = db.relationship('Purchase', backref='buyer', lazy='dynamic', foreign_keys='Purchase.user_id')
    
    favorited = db.relationship(
        'Announcement', secondary=favorites,
        backref=db.backref('fans', lazy='dynamic'), lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_favorited(self, announcement):
        return self.favorited.filter(
            favorites.c.announcement_id == announcement.id).count() > 0

    def add_favorite(self, announcement):
        if not self.is_favorited(announcement):
            self.favorited.append(announcement)

    def remove_favorite(self, announcement):
        if self.is_favorited(announcement):
            self.favorited.remove(announcement)
            
    def __repr__(self):
        return f'<User {self.username}>'

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    announcements = db.relationship('Announcement', backref='category', lazy='dynamic')

    def __repr__(self):
        return f'<Category {self.name}>'

class Announcement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    
    # Chaves estrangeiras
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))

    # Relações
    questions = db.relationship('Question', backref='announcement', lazy='dynamic', cascade="all, delete-orphan")
    purchase = db.relationship('Purchase', backref='announcement', uselist=False) # Um anúncio só pode ter uma compra

    def __repr__(self):
        return f'<Announcement {self.title}>'

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    answer = db.Column(db.Text, nullable=True) # A resposta do vendedor
    answer_timestamp = db.Column(db.DateTime, nullable=True)

    # Chaves estrangeiras
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) # Quem perguntou
    announcement_id = db.Column(db.Integer, db.ForeignKey('announcement.id'))

    def __repr__(self):
        return f'<Question {self.body[:50]}...>'

class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    
    # Chaves estrangeiras
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) # Quem comprou
    announcement_id = db.Column(db.Integer, db.ForeignKey('announcement.id'), unique=True) # O anúncio comprado
    
    def __repr__(self):
        return f'<Purchase of announcement {self.announcement_id} by user {self.user_id}>'
