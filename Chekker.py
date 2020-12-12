import os
from flask import Flask, abort, redirect, request, render_template
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from slimish_jinja import SlimishExtension
from flask_assets import Environment, Bundle
from data import db_session
from data.models.user import *
from data.models.labour import *
from data.models.test import *
from data.models.answer import *
from forms.create_labour import *
from forms.labour_create_test import *
from forms.test_create_answer import *
from forms.login import *
from Constants import *
from functools import wraps

app = Flask(__name__)

app.config['SECRET_KEY'] = 'chekker_secret_key'
app.config['DATABASE_URI'] = DATABASE_URI

app.jinja_options['extensions'].append(SlimishExtension)

assets = Environment(app)
assets.url = "/static"
sass = Bundle("css/sass/style.sass", filters="libsass",
              output="css/style.css", depends='**/*.sass')
assets.register('sass', sass)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.anonymous_user = ChekkerAnonymousUser


def admin_required(func):
    @wraps(func)
    def new_func(*args, **kwargs):
        if current_user.is_admin():
            return func(*args, **kwargs)
        if not current_user.is_authenticated:
            return redirect(f"/login?next={request.path}")
        abort(403)
    return new_func


def teacher_required(func):
    @wraps(func)
    def new_func(*args, **kwargs):
        if current_user.is_teacher():
            return func(*args, **kwargs)
        if not current_user.is_authenticated:
            return redirect(f"/login?next={request.path}")
        abort(403)
    return new_func


@app.route("/")
def index():
    return render_template("base.slim", title="Chekker")


@app.route("/labours")
def labours():
    session = db_session.create_session()

    labours = session.query(Labour).all()
    return render_template("labours.slim", title="Работы", labours=labours)


@app.route("/labours/<int:labour_id>")
def labour(labour_id):
    session = db_session.create_session()

    labour = session.query(Labour).get(labour_id)
    if not labour:
        abort(404)

    return render_template("labour.slim", title=labour.description)


@app.route("/labours/<int:labour_id>/perform", methods=["GET", "POST"])
def perform_labour(labour_id):
    session = db_session.create_session()

    labour = session.query(Labour).get(labour_id)
    if not labour:
        abort(404)

    return render_template("perform_labour.slim", title=labour.description)


@app.route("/labours/create", methods=["GET", "POST"])
@teacher_required
def labour_create():
    session = db_session.create_session()
    form = CreateLabourForm()

    if form.validate_on_submit():
        labour = Labour()
        labour.title = form.description.data.strip()
        labour.description = form.description.data.strip()
        labour.start_date = form.start_date.data
        labour.end_date = form.end_date.data

        session.add(labour)
        session.commit()

        return redirect(f"/labours/{labour.id}")

    return render_template("labour_create.slim", title="Создать работу", form=form)


@app.route("/labours/<int:labour_id>/edit", methods=["GET", "POST"])
@teacher_required
def labour_edit(labour_id):
    session = db_session.create_session()

    labour = session.query(Labour).get(labour_id)
    if not labour:
        abort(404)

    form = CreateLabourForm()

    if form.validate_on_submit():
        labour.title = form.description.data.strip()
        labour.description = form.description.data.strip()
        labour.start_date = form.start_date.data
        labour.end_date = form.end_date.data

        session.commit()

        return redirect(f"/labours/{labour.id}")

    form.description.data = labour.title
    form.description.data = labour.description
    form.start_date.data = labour.start_date
    form.end_date.data = labour.end_date

    return render_template("labour_edit.slim", title="Редактировать работу", form=form)


@app.route("/labours/<int:labour_id>/delete", methods=["GET"])
@teacher_required
def labour_delete(labour_id):
    session = db_session.create_session()

    labour = session.query(Labour).get(labour_id)
    if not labour:
        abort(404)

    session.delete(labour)
    session.commit()

    return redirect("/labours")


@app.route("/labours/<int:labour_id>/tests/create")
@teacher_required
def labour_create_test(labour_id):
    session = db_session.create_session()

    labour = session.query(Labour).get(labour_id)
    if not labour:
        abort(404)

    form = LabourCreateTestForm()

    if form.validate_on_submit():
        test = Test()
        test.labour = labour
        test.statement = form.statement.data
        test.answer_type = form.answer_type.data

        session.add(test)
        session.commit()

        return redirect(f"/labours/{labour.id}")

    return render_template("labour_create_test.slim", title="Добавить вопрос", form=form)


@app.route("/labours/<int:labour_id>/tests/<int:test_id>/edit")
@teacher_required
def labour_edit_test(labour_id, test_id):
    session = db_session.create_session()

    labour = session.query(Labour).get(labour_id)
    if not labour:
        abort(404)

    test = session.query(Test).get(test_id)
    if not test:
        abort(404)

    if test.labour != labour:
        abort(404)

    form = LabourCreateTestForm()

    if form.validate_on_submit():
        test.statement = form.statement.data
        test.answer_type = form.answer_type.data

        session.add(test)
        session.commit()

        return redirect(f"/labours/{labour.id}")

    form.statement.data = test.statement
    form.answer_type.data = test.answer_type

    return render_template("labour_create_test.slim", title="Редактировать вопрос", form=form)


@app.route("/labours/<int:labour_id>/tests/<int:test_id>/delete")
@teacher_required
def labour_delete_test(labour_id, test_id):
    session = db_session.create_session()

    labour = session.query(Labour).get(labour_id)
    if not labour:
        abort(404)

    test = session.query(Test).get(test_id)
    if not test:
        abort(404)

    if test.labour != labour:
        abort(404)

    session.delete(test)
    session.commit()

    return redirect(f"/labours/{labour.id}")


@app.route("/labours/<int:labour_id>/tests/<int:test_id>/answers/create")
def test_create_answer(labour_id, test_id):
    session = db_session.create_session()

    labour = session.query(Labour).get(labour_id)
    if not labour:
        abort(404)

    test = session.query(Test).get(test_id)
    if not test:
        abort(404)

    if test.labour != labour:
        abort(404)

    form = TestCreateAnswerForm()

    if form.validate_on_submit():
        answer = Answer()
        answer.test = test

        answer.data = form.data.data.strip()
        answer.is_correct = form.is_correct.data

        session.add(answer)
        session.commit()

        return redirect(f"/labours/{labour.id}")

    return render_template("test_create_answer.slim", title="Добавить ответ", form=form)


@app.route("/labours/<int:labour_id>/tests/<int:test_id>/answers/<int:answer_id>/edit")
def test_edit_answer(labour_id, test_id, answer_id):
    session = db_session.create_session()

    labour = session.query(Labour).get(labour_id)
    if not labour:
        abort(404)

    test = session.query(Test).get(test_id)
    if not test:
        abort(404)

    answer = session.query(Answer).get(answer_id)
    if not answer:
        abort(404)

    if test.labour != labour:
        abort(404)

    if answer.test != test:
        abort(404)

    form = TestCreateAnswerForm()

    if form.validate_on_submit():
        answer.data = form.data.data.strip()
        answer.is_correct = form.is_correct.data

        session.commit()

        return redirect(f"/labours/{labour.id}")

    form.data.data = answer.data
    form.is_correct.data = answer.is_correct

    return render_template("test_create_answer.slim", title="Редактировать ответ", form=form)


@app.route("/labours/<int:labour_id>/tests/<int:test_id>/answers/<int:answer_id>/delete")
def test_delete_answer(labour_id, test_id, answer_id):
    session = db_session.create_session()

    labour = session.query(Labour).get(labour_id)
    if not labour:
        abort(404)

    test = session.query(Test).get(test_id)
    if not test:
        abort(404)

    answer = session.query(Answer).get(answer_id)
    if not answer:
        abort(404)

    if test.labour != labour:
        abort(404)

    if answer.test != test:
        abort(404)

    session.delete(answer)
    session.commit()

    return redirect(f"/labours/{labour.id}")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()

        user = session.query(User).filter(User.login == form.login.data).first()

        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data, duration=datetime.timedelta(days=7))

            return redirect(request.args.get('next') or '/')

        return render_template('login.html',
                               message="Неправильный логин или пароль.",
                               form=form)

    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(request.args.get('next') or '/')


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


if __name__ == '__main__':
    os.chdir(APP_ROOT)
    db_session.global_init(app.config['DATABASE_URI'])

    app.run(port=APP_PORT, host='0.0.0.0')
