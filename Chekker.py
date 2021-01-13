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
from data.models.attachment import *
from forms.create_labour import *
from forms.labour_create_test import *
from forms.test_create_answer import *
from forms.test_upload_attachment import *
from forms.login import *
from lib import AnswerTypes
from lib.AnswerTypes import *
from lib import AttachmentTypes
from Constants import *
from functools import wraps
from werkzeug.utils import secure_filename
from uuid import uuid4

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


def format_answer(answer):
    # Форматирование строки, чтобы пробел в конце не убивал ответ
    answer = answer.strip()
    answer = answer.replace(" ", "")
    answer = answer.lower()

    return answer


@app.context_processor
def context_processor():
    # Передача важных переменных в шаблоны
    return dict(ANSWER_TYPES=ANSWER_TYPES, AnswerTypes=AnswerTypes,
                ATTACHMENT_TYPES=AttachmentTypes.ATTACHMENT_TYPES, AttachmentTypes=AttachmentTypes)


@app.errorhandler(403)
def not_found(error):
    # Контроллер для ошибки 403
    return render_template("error.html", code=403, message="Вам сюда нельзя!")


@app.errorhandler(404)
def not_found(error):
    # Контроллер для ошибки 404
    return render_template("error.html", code=404, message="Такой страницы нет. Но есть много других!")


@app.errorhandler(500)
def not_found(error):
    # Контроллер для ошибки 500
    return render_template("error.html", code=500, message="Проблема не в вас, проблема — в нас. Обещаем исправиться.")


def admin_required(func):
    # Декоратор, который пускает в страницу только администраторов. Ставится перед функцией-контроллером
    @wraps(func)
    def new_func(*args, **kwargs):
        if current_user.is_admin():
            return func(*args, **kwargs)
        if not current_user.is_authenticated:
            return redirect(f"/login?next={request.path}")
        abort(403)
    return new_func


def teacher_required(func):
    # Декоратор, который пускает в страницу только учителей (ну и администраторов). Ставится перед функцией-контроллером
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
    # Главная страница
    return render_template("index.html", title="Chekker")


@app.route("/labours")
def labours():
    # Страница всех работ
    session = db_session.create_session()

    labours = session.query(Labour).order_by(Labour.id.desc()).all()
    return render_template("labours.html", title="Работы", labours=labours)


@app.route("/labours/<int:labour_id>")
def labour(labour_id):
    # Страница одной работы
    session = db_session.create_session()

    labour = session.query(Labour).get(labour_id)
    if not labour:
        abort(404)

    return render_template("labour.html", labour=labour,    title=labour.title)


@app.route("/labours/<int:labour_id>/perform", methods=["GET", "POST"])
@login_required
def labour_perform(labour_id):
    # Страница выполнения работы
    session = db_session.create_session()

    labour = session.query(Labour).get(labour_id)
    if not labour:
        abort(404)

    if not labour.is_active():
        return redirect(f"/labours/{labour.id}")

    labour_association = session.query(UserToLabour).get((current_user.id, labour.id))
    if labour_association:
        return redirect("/results")

    if request.method == "GET":
        return render_template("labour_perform.html", title=labour.title, labour=labour)

    count = 0
    # Проверка всех ответов исходя из правильных ответов в БД
    for test in labour.tests:
        user_answers = request.form
        if test.answer_type in [AnswerTypes.ManualInput().get_id(), AnswerTypes.SingleAnswer().get_id()]:
            # Здесь проверяем, что ответ точно совпадает с правильным
            user_answers = user_answers.getlist(str(test.id))
            user_answers = list(map(format_answer, user_answers))

            if not user_answers:
                user_answer = ''
            else:
                user_answer = format_answer(user_answers[0])

            test_association = UserToTest()
            test_association.user = current_user
            test_association.test = test
            test_association.chosen_answer = user_answer

            correct_answers = map(lambda x: x.data, test.get_correct_answers())

            if user_answer in correct_answers:
                test_association.is_correct = True
                count += 1

            session.add(test_association)
        elif test.answer_type == AnswerTypes.MultiplyAnswer().get_id():
            # Здесь проверяем, что отмечены все правильные ответы, а неправильные не отмечены
            user_answers = user_answers.getlist(str(test.id))
            user_answers = list(map(format_answer, user_answers))

            test_association = UserToTest()
            test_association.user = current_user
            test_association.test = test
            test_association.chosen_answer = '; '.join(user_answers)

            correct_answers = test.get_correct_answers()

            if user_answers == list(map(lambda x: x.data, correct_answers)):
                test_association.is_correct = True
                count += 1

            session.add(test_association)

    # Выставляем баллы
    labour_association = UserToLabour()
    labour_association.user = current_user
    labour_association.labour = labour
    labour_association.result = count

    session.add(labour_association)
    session.commit()

    return redirect("/results")


@app.route("/results")
@login_required
def results():
    # Просмотр всех своих результатов
    session = db_session.create_session()

    results = session.query(UserToLabour).filter(UserToLabour.user == current_user).all()

    return render_template("results.html", title="Мои результаты", results=results)


@app.route("/labours/<int:labour_id>/results")
@login_required
def labour_results(labour_id):
    # Просмотр результатов одной работы после её окончания (ну или в любое время для учителей)
    session = db_session.create_session()

    labour = session.query(Labour).get(labour_id)
    if not labour:
        abort(404)

    if not labour.is_finished() and not current_user.is_teacher():
        return redirect(f"/labours/{labour.id}")

    labour_association = session.query(UserToLabour).get((current_user.id, labour.id))
    if not labour_association:
        return redirect(f"/labours/{labour.id}")

    return render_template("labour_results.html", title="Результаты работы", labour=labour,
                           labour_association=labour_association)


@app.route("/labours/<int:labour_id>/results/all")
@teacher_required
def labour_results_all(labour_id):
    # Просмотр таблицы результатов по работе для учителя (сводная статистика)
    session = db_session.create_session()

    labour = session.query(Labour).get(labour_id)
    if not labour:
        abort(404)

    results = session.query(UserToLabour).filter(UserToLabour.labour == labour).all()
    results.sort(key=lambda x: -x.result)

    return render_template("labour_results_all.html", title="Все результаты", labour=labour, results=results)


@app.route("/labours/create", methods=["GET", "POST"])
@teacher_required
def labour_create():
    # Создание работы
    session = db_session.create_session()
    form = CreateLabourForm()

    if form.validate_on_submit():
        labour = Labour()
        labour.title = form.title.data.strip()
        labour.description = form.description.data.strip()
        labour.start_date = form.start_date.data
        labour.end_date = form.end_date.data

        session.add(labour)
        session.commit()

        return redirect(f"/labours/{labour.id}")

    return render_template("labour_create.html", title="Создать работу", form=form)


@app.route("/labours/<int:labour_id>/edit", methods=["GET", "POST"])
@teacher_required
def labour_edit(labour_id):
    # Редактирование работы
    session = db_session.create_session()

    labour = session.query(Labour).get(labour_id)
    if not labour:
        abort(404)

    form = CreateLabourForm()

    if form.validate_on_submit():
        labour.title = form.title.data.strip()
        labour.description = form.description.data.strip()
        labour.start_date = form.start_date.data
        labour.end_date = form.end_date.data

        session.commit()

        return redirect(f"/labours/{labour.id}")

    form.title.data = labour.title
    form.description.data = labour.description
    form.start_date.data = labour.start_date
    form.end_date.data = labour.end_date

    return render_template("labour_create.html", title="Редактировать работу", form=form)


@app.route("/labours/<int:labour_id>/delete", methods=["GET"])
@teacher_required
def labour_delete(labour_id):
    # Удаление работы
    session = db_session.create_session()

    labour = session.query(Labour).get(labour_id)
    if not labour:
        abort(404)

    session.delete(labour)
    session.commit()

    return redirect("/labours")


@app.route("/labours/<int:labour_id>/tests/create", methods=["GET", "POST"])
@teacher_required
def labour_create_test(labour_id):
    # Создание вопроса в работе
    session = db_session.create_session()

    labour = session.query(Labour).get(labour_id)
    if not labour:
        abort(404)

    form = LabourCreateTestForm()

    if form.validate_on_submit():
        test = Test()
        test.labour = labour
        test.statement = form.statement.data.strip()
        test.answer_type = form.answer_type.data

        session.add(test)
        session.commit()

        return redirect(f"/labours/{labour.id}#q{test.id}")

    return render_template("labour_create_test.html", title="Добавить вопрос", form=form)


@app.route("/labours/<int:labour_id>/tests/<int:test_id>/edit", methods=["GET", "POST"])
@teacher_required
def labour_edit_test(labour_id, test_id):
    # Редактирование вопроса в работе
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
        test.statement = form.statement.data.strip()
        test.answer_type = form.answer_type.data

        session.add(test)
        session.commit()

        return redirect(f"/labours/{labour.id}#q{test.id}")

    form.statement.data = test.statement
    form.answer_type.data = test.answer_type

    return render_template("labour_create_test.html", title="Редактировать вопрос", form=form)


@app.route("/labours/<int:labour_id>/tests/<int:test_id>/delete")
@teacher_required
def labour_delete_test(labour_id, test_id):
    # Удаление вопроса в работе
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

    return redirect(f"/labours/{labour.id}#question-block")


@app.route("/labours/<int:labour_id>/tests/<int:test_id>/attachments/upload", methods=["GET", "POST"])
@teacher_required
def test_upload_attachment(labour_id, test_id):
    # Загрузка вложения к вопросу
    session = db_session.create_session()

    labour = session.query(Labour).get(labour_id)
    if not labour:
        abort(404)

    test = session.query(Test).get(test_id)
    if not test:
        abort(404)

    if test.labour != labour:
        abort(404)

    form = TestUploadAttachmentForm()

    if form.validate_on_submit():
        file = form.image.data
        filename = secure_filename(str(uuid4()) + "." + file.filename.split(".")[-1])

        short_folder = "static/attachments"
        short_path = os.path.join(short_folder, filename)

        path = os.path.join(APP_ROOT, short_path)
        file.save(path)

        attachment = Attachment()
        attachment.test = test
        attachment.type = AttachmentTypes.ImageAttachment().get_id()
        attachment.link = short_path

        session.add(attachment)
        session.commit()

        return redirect(f"/labours/{labour.id}#q{test.id}")

    return render_template("test_upload_attachment.html", title="Загрузить вложение", form=form)


@app.route("/labours/<int:labour_id>/tests/<int:test_id>/attachments/<int:attachment_id>/delete", methods=["GET", "POST"])
@teacher_required
def test_delete_attachment(labour_id, test_id, attachment_id):
    # Удаление вложения
    session = db_session.create_session()

    labour = session.query(Labour).get(labour_id)
    if not labour:
        abort(404)

    test = session.query(Test).get(test_id)
    if not test or test.labour != labour:
        abort(404)

    attachment = session.query(Attachment).get(attachment_id)
    if not attachment or attachment.test != test:
        abort(404)

    try:
        os.remove(attachment.link)
    except Exception as e:
        pass
    finally:
        session.delete(attachment)

    session.commit()

    return redirect(f"/labours/{labour.id}#q{test.id}")


@app.route("/labours/<int:labour_id>/tests/<int:test_id>/answers/create", methods=["GET", "POST"])
def test_create_answer(labour_id, test_id):
    # Создание ответа на вопрос
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

        answer.data = format_answer(form.data.data)
        answer.is_correct = form.is_correct.data

        session.add(answer)
        session.commit()

        return redirect(f"/labours/{labour.id}#q{test.id}")

    return render_template("test_create_answer.html", title="Добавить ответ", form=form)


@app.route("/labours/<int:labour_id>/tests/<int:test_id>/answers/<int:answer_id>/edit", methods=["GET", "POST"])
def test_edit_answer(labour_id, test_id, answer_id):
    # Редактирование ответа на вопрос
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
        answer.data = format_answer(form.data.data)
        answer.is_correct = form.is_correct.data

        session.commit()

        return redirect(f"/labours/{labour.id}#q{test.id}")

    form.data.data = answer.data
    form.is_correct.data = answer.is_correct

    return render_template("test_create_answer.html", title="Редактировать ответ", form=form)


@app.route("/labours/<int:labour_id>/tests/<int:test_id>/answers/<int:answer_id>/delete")
def test_delete_answer(labour_id, test_id, answer_id):
    # Удаление ответа на вопрос
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

    return redirect(f"/labours/{labour.id}#q{test.id}")


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Вход в систему
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


@app.route("/classes")
def classes():
    # Просмотр классов. Пока что не реализовано, там заглушка
    return render_template("classes.html", title="Классы")


@app.route('/logout')
@login_required
def logout():
    # Выход из системы
    logout_user()
    return redirect(request.args.get('next') or '/')


@login_manager.user_loader
def load_user(user_id):
    # Системная функция для подгрузки текущего пользователя в шаблон
    session = db_session.create_session()
    return session.query(User).get(user_id)


if __name__ == '__main__':
    # Перемещение в директорию проекта (нужно для лучшей стабильности)
    try:
        os.chdir(APP_ROOT)
    except Exception as e:
        pass

    # Подключаемся к БД
    db_session.global_init(app.config['DATABASE_URI'])

    # Запускаем приложение
    app.run(port=APP_PORT, host='0.0.0.0')
