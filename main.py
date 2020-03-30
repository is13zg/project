from flask import Flask, render_template, redirect, request, make_response, jsonify, flash, abort
from data import db_session, news_api
import datetime
from data.users import User
from data.news import News
from data.likes import Likes
from data.comments import Comments

from data.forms import RegisterForm, LoginForm, NewsForm, SortForm, FilterForm, CommentForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user



db_session.global_init("/db/blogs.sqlite")
app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.register_blueprint(news_api.blueprint)
global sorting, filtering
sorting = "1"
filtering = "1"


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


@app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    session = db_session.create_session()
    news = session.query(News).filter(News.id == id,
                                      News.user == current_user).first()
    if news:
        session.delete(news)
        session.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


def count_rate(news_id, data_s=0, data_f=0):
    rate = 0
    if data_f == data_s:
        session = db_session.create_session()
        likes = session.query(Likes).filter(Likes.news_id == news_id)
        for like in likes:
            rate += like.like_point
    else:
        pass
        # count rate in date
    return rate


@app.route("/", methods=['GET', 'POST'])
def index():
    global sorting, filtering

    form = SortForm()
    form2 = FilterForm()

    if form.submit() and form.sort.data != "None":
        sorting = form.sort.data

    if form2.submit() and form2.filter.data != "None":
        filtering = form2.filter.data

    session = db_session.create_session()

    if filtering == "1":
        filter_date = datetime.datetime.now() - datetime.timedelta(weeks=1)
    elif filtering == "2":
        filter_date = datetime.datetime.now() - datetime.timedelta(days=30)
    else:
        filter_date = datetime.datetime.now() - datetime.timedelta(days=5000)

    if current_user.is_authenticated:
        news = session.query(News).filter(
            (News.user == current_user) | (News.is_private != True)).filter(News.created_date > filter_date)
    else:
        news = session.query(News).filter(News.is_private != True).filter(News.created_date > filter_date)

    ls = []
    for one_news in news:
        x = one_news.to_dict(only=('id', 'title', 'content', 'user.name', 'user.id', 'created_date'))
        x['rate'] = count_rate(x['id'])
        comments = session.query(Comments).filter(Comments.news_id == x['id'])
        x['comments'] = [i.to_dict(only=('text', 'user.name', 'created_date')) for i in comments]
        ls.append(x)

    if sorting == "1":
        ls.sort(key=lambda x: x['rate'], reverse=True)
    elif sorting == "2":
        ls.sort(key=lambda x: x['created_date'], reverse=True)

    form.sort.default = sorting
    form2.filter.default = filtering
    form.process()
    form2.process()

    return render_template("index.html", news=ls, form=form, form2=form2)


@app.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = NewsForm()
    if request.method == "GET":
        session = db_session.create_session()
        news = session.query(News).filter(News.id == id,
                                          News.user == current_user).first()
        if news:
            form.title.data = news.title
            form.content.data = news.content
            form.is_private.data = news.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        session = db_session.create_session()
        news = session.query(News).filter(News.id == id,
                                          News.user == current_user).first()
        if news:
            news.title = form.title.data
            news.content = form.content.data
            news.is_private = form.is_private.data
            session.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('news.html', title='Редактирование новости', form=form)


@app.route('/news', methods=['GET', 'POST'])
@login_required
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        news = News()
        news.title = form.title.data
        news.content = form.content.data
        news.is_private = form.is_private.data
        current_user.news.append(news)
        session.merge(current_user)
        session.commit()
        return redirect('/')
    return render_template('news.html', title='Добавление новости',
                           form=form)


@app.route('/add_comment/<int:id>', methods=['GET', 'POST'])
@login_required
def add_comment(id):
    form = CommentForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        comment = Comments()
        comment.text = form.text.data
        comment.news_id = id
        current_user.comments.append(comment)
        session.merge(current_user)
        session.commit()
        return redirect('/')
    return render_template('comments.html', title='Добавление комментария',
                           form=form)


def like(id, point):
    print("point= ", point)
    session = db_session.create_session()
    news = session.query(News).filter(News.id == id,
                                      News.user == current_user).first()
    like = session.query(Likes).filter(Likes.news_id == id, Likes.user_id == current_user.id).first()

    if not like:
        like = Likes()
        like.like_point = point
        like.user_id = current_user.id
        like.news_id = id
        session.add(like)
    else:
        if like.like_point == point:
            flash("you already did it")
        else:
            like.like_point = point
            session.merge(like)

    session.commit()


@app.route('/like/<int:id>', methods=['GET', 'POST'])
@login_required
def add_like(id):
    like(id, 1)
    return redirect('/')


@app.route('/dislike/<int:id>', methods=['GET', 'POST'])
@login_required
def add_dislike(id):
    like(id, -1)
    return redirect('/')


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        session = db_session.create_session()
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)
