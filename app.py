from flask import Flask, render_template, request, redirect, make_response, flash
from flask_sqlalchemy import SQLAlchemy
from form import searchForm, LoginForm, RegisterForm
from flask_login import LoginManager, login_user, UserMixin, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
import pdfkit


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///student.db'
db = SQLAlchemy(app)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY']=SECRET_KEY
path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    number_certificate = db.Column(db.String(300), nullable=True)
    full_student_name = db.Column(db.String(300), nullable=True)
    full_teacher_name = db.Column(db.String(300), nullable=True)
    name_course = db.Column(db.String(300), nullable=True)
    date_start = db.Column(db.String(300), nullable=True)
    date_finish = db.Column(db.String(300), nullable=True)
    num_of_hours = db.Column(db.Integer, nullable=True)
    program_course = db.Column(db.String(300), nullable=True)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    email = db.Column(db.String(300), nullable=True, unique=True)
    name = db.Column(db.String(300), nullable=True)
    password = db.Column(db.String(300), nullable=True)
    password2 = db.Column(db.String(300), nullable=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template("main.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=True)
                return render_template("main.html", form=form)
        return "Invalid data"
    return render_template("login.html", form=form)


@app.route('/signup', methods=['POST', 'GET'])
@login_required
def signup():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(email = form.email.data, name = form.name.data, password = hashed_password, password2 = hashed_password)
        if form.password.data == form.password2.data:
            db.session.add(new_user)
            db.session.commit()
            print("New user has been created")
            return redirect('/')
        else:
            return "There is two different passwords"
    return render_template("signup.html", form=form)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    print("You've been logged out")
    return redirect('/login')


@app.route('/database')
def database():
    students = Student.query.order_by(Student.id).all()
    return render_template("database.html", students=students)

@app.route('/database/<int:id>/del')
@login_required
def data_delete(id):
    student = Student.query.get_or_404(id)

    try:
        db.session.delete(student)
        db.session.commit()
        return redirect('/database')
    except:
        return "There is an error while deleting the data"

@app.route('/search', methods=['GET', 'POST'])
def search():
    form = searchForm()
    students = Student.query
    if form.validate_on_submit():
        #Query the Database
        students = students.filter(Student.number_certificate.like('%' + form.searched.data + '%'))

        students = students.order_by(Student.id).all()

    return render_template("search.html", students=students)

@app.context_processor
def base():
    form = searchForm()
    return  dict(form=form)

@app.route('/database/<int:id>/update', methods =['POST', 'GET'])
@login_required
def data_update(id):
    student = Student.query.get(id)
    if request.method == "POST":
        student.number_certificate = request.form['number_certificate']
        student.full_student_name = request.form['full_student_name']
        student.full_teacher_name = request.form['full_teacher_name']
        student.name_course = request.form['name_course']
        student.date_start = request.form['date_start']
        student.date_finish = request.form['date_finish']
        student.num_of_hours = request.form['num_of_hours']
        student.program_course = request.form['program_course']

        try:
            db.session.commit()
            return redirect('/database')
        except:
            return "There is an error when you try to update data."
    else:
        return render_template("dataupdate.html", student=student)

@app.route('/database/<int:id>')
def data_id(id):
    student = Student.query.get(id)
    return render_template("datadetail.html", student=student)

@app.route('/database/<int:id>/downloadpdf')
def generate(id):
    student = Student.query.get_or_404(id)
    res = render_template('datadownload.html', student=student)
    responsestring = pdfkit.from_string(res, False, configuration=config)
    response = make_response(responsestring)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment;filename=output.pdf'
    return response

@app.route('/insert_data', methods=['POST', 'GET'])
@login_required
def data():
    if request.method == "POST":
        number_certificate = request.form['number_certificate']
        full_student_name = request.form['full_student_name']
        full_teacher_name = request.form['full_teacher_name']
        name_course = request.form['name_course']
        date_start = request.form['date_start']
        date_finish = request.form['date_finish']
        num_of_hours = request.form['num_of_hours']
        program_course = request.form['program_course']

        student = Student(number_certificate=number_certificate, full_student_name=full_student_name, full_teacher_name=full_teacher_name, name_course=name_course, date_start=date_start, date_finish=date_finish, num_of_hours=num_of_hours, program_course=program_course)

        try:
            db.session.add(student)
            db.session.commit()
            return redirect('/database')
        except:
            return "There is an error when you try to add data."
    else:
        return render_template("insert_data.html")

if __name__ == "__main__":
    app.run(debug=True)