from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField, StringField, PasswordField, BooleanField, SelectField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    name = StringField('Имя пользователя', validators=[DataRequired()])
    about = TextAreaField("Немного о себе")
    submit = SubmitField('Войти')


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class NewsForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    content = TextAreaField("Содержание")
    is_private = BooleanField("Личное")
    submit = SubmitField('Применить')


class SortForm(FlaskForm):
    sort = SelectField('Сортировка', choices=[('1', 'По рейтингу'), ('2', 'По дате')])
    submit = SubmitField('Сортировка')


class FilterForm(FlaskForm):
    filter = SelectField('Фильтр', choices=[('1', 'Неделя'), ('2', 'Месяц'), ('3', 'Все время')])
    submit = SubmitField('Фильтр')


class CommentForm(FlaskForm):
    text = TextAreaField("Содержание", validators=[DataRequired()])
    submit = SubmitField('Применить')
