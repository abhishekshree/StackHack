from flask import Flask, render_template, redirect, url_for, request, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FileField, SubmitField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, InputRequired, Length
from flask_wtf.file import FileRequired, FileAllowed
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import asc, desc
import os
import glob
import random
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bootstrap import Bootstrap


app = Flask(__name__)
db = SQLAlchemy(app)
Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

app.config['SECRET_KEY'] = 'you-will-never-guess'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'


class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(80))


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


class Register(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    RegistrationNumber = db.Column(db.String(80))
    Name = db.Column(db.String(80))
    Email = db.Column(db.String(120))
    desc = db.Column(db.String(200))
    Type = db.Column(db.String(20))
    tickets = db.Column(db.Integer)
    filename = db.Column(db.String(100))
    RegisterDate = db.Column(db.Date())


class RegisterForm(FlaskForm):
    firstName = StringField("First Name", validators=[DataRequired()])
    lastName = StringField("Last Name", validators=[DataRequired()])
    describe = StringField('Description', validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    tickets = StringField("Number of Tickets", validators=[DataRequired()])
    Regtype = SelectField('Choose your option', choices=[
                          ('1', 'Self'), ('2', 'Group'), ('3', 'Corporate'), ('4', 'Others')])
    file = FileField(validators=[FileRequired(),
                                 FileAllowed(['jpeg', 'png'], 'Images only!')])
    submit = SubmitField()


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[
                           InputRequired(), Length(min=4, max=15)])
    password = PasswordField("Password", validators=[
                             InputRequired(), Length(min=8, max=80)])


class SignupForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired()])
    username = StringField("Username", validators=[
                           InputRequired(), Length(min=4, max=15)])
    password = PasswordField("Password", validators=[
                             InputRequired(), Length(min=8, max=80)])


@app.route('/')
def index():
    events = Register.query.order_by(Register.id.desc()).limit(5)
    return render_template('index.html', events=events)


@app.route('/form', methods=['GET', 'POST'])
def form():
    form = RegisterForm()
    regtypes = ['Self', 'Group', 'Corporate', 'Others']
    if request.method == 'POST':
        name = form.firstName.data + " " + form.lastName.data
        email = form.email.data
        ticketcount = form.tickets.data
        desc = form.describe.data
        # file = form.file.data
        file = request.files['file']
        regtype = regtypes[int(form.Regtype.data)-1]
        regno = name[:1] + str(random.randint(10000, 1000000000))
        file.save(os.path.join(os.getcwd()+'static/images',
                               secure_filename(file.filename)))

        context = {
            'name': name,
            'email': email,
            'desc': desc,
            'ticket': ticketcount,
            'type': regtype,
            'file': file.filename,
            'reg': regno
        }
        return redirect(url_for('preview', context=context))
        # return context

    return render_template('form.html', form=form)


@app.route('/preview/', methods=['GET', 'POST'])
def preview():
    dict = eval(request.args.get('context', None))
    if request.method == 'POST':
        os.rename(os.getcwd() +"static/images/" + dict['file'], os.getcwd()+
                  "static/identities/" + dict['file'])
        new_register = Register(
            RegistrationNumber=dict['reg'],
            Name=dict['name'],
            Email=dict['email'],
            desc=dict['desc'],
            Type=dict['type'],
            tickets=dict['ticket'],
            filename=dict['file'],
            RegisterDate=datetime.datetime.now()
        )
        db.session.add(new_register)
        db.session.commit()

        return redirect(url_for('thanks'))

    return render_template('preview.html', context=dict)


@app.route('/revert')
def revert():
    files = glob.glob('static/images/*')
    for f in files:
        os.remove(f)
    return redirect(url_for('form'))


@app.route('/help')
def help():
    return render_template('help.html')


@app.route('/thanks')
def thanks():
    return render_template('thanks.html')


@app.route('/all')
def all():
    events = Register.query.all()[::-1]
    return render_template('all.html', events=events)


@app.route('/delete/<int:id>')
@login_required
def delete(id):
    r = Register.query.get_or_404(id)
    path = ('static/identities/' + r.filename).strip()
    os.remove(path)
    db.session.delete(r)
    db.session.commit()

    return redirect(url_for('dashboard'))

# login


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('dashboard'))
        return '''<h1>Invalid username or password</h1><script>
        window.setTimeout(function () {

            window.location.href = "";

        }, 2000);
    </script>'''

    return render_template('login.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
@login_required
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        hashed = generate_password_hash(form.password.data, method='sha256')
        new_user = Users(username=form.username.data,
                         email=form.email.data, password=hashed)
        db.session.add(new_user)
        db.session.commit()
        return '''<h1>New user added </h1> <script>
        window.setTimeout(function () {

            window.location.href = "/";

        }, 2000);
    </script>'''
    return render_template('signup.html', form=form)


@app.route('/dashboard')
@login_required
def dashboard():
    events = Register.query.all()[::-1]
    return render_template('dashboard.html', events=events, name=current_user.username)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run()