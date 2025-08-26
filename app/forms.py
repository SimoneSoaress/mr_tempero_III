# app/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, FloatField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired()])
    password = PasswordField('Senha', validators=[DataRequired()])
    remember_me = BooleanField('Lembrar-me')
    submit = SubmitField('Entrar')

class RegistrationForm(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired()])
    password2 = PasswordField(
        'Repetir Senha', validators=[DataRequired(), EqualTo('password', message='As senhas devem ser iguais.')])
    submit = SubmitField('Registar')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Este nome de usuário já existe.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Este email já está sendo utilizado.')

class AnnouncementForm(FlaskForm):
    title = StringField('Título do Anúncio', validators=[DataRequired(), Length(min=5, max=140)])
    description = TextAreaField('Descrição', validators=[DataRequired()])
    price = FloatField('Preço', validators=[DataRequired()])
    category_id = SelectField('Categoria', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Publicar Anúncio')

class CategoryForm(FlaskForm):
    name = StringField('Nome da Categoria', validators=[DataRequired(), Length(min=3, max=100)])
    submit = SubmitField('Salvar Categoria')

class QuestionForm(FlaskForm):
    body = TextAreaField('A sua pergunta', validators=[DataRequired(), Length(min=10, max=500)])
    submit = SubmitField('Enviar Pergunta')
    
class AnswerForm(FlaskForm):
    answer = TextAreaField('A sua resposta', validators=[DataRequired(), Length(min=10, max=500)])
    submit = SubmitField('Enviar Resposta')
