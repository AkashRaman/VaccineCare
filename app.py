from flask import Flask, render_template, url_for, request, redirect
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField
from wtforms.validators import InputRequired,Length,ValidationError
from flask_bcrypt import Bcrypt
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
app.config['SECRET_KEY'] = 'thisisasecretkey'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Center(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    hospital = db.Column(db.String(200), nullable = False)
    working_hours = db.Column(db.String(200), nullable = False)
    location = db.Column(db.String(200), nullable = False)
    registered_date = db.Column(db.DateTime, default = datetime.utcnow)

    def __repr__(self):
        return '<Centers %r>' % self.id 

class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(200), nullable = False)
    age = db.Column(db.Integer, nullable = False)
    location = db.Column(db.String(200), nullable = False)
    mobile_number = db.Column(db.Integer, nullable = False)
    mobile_number_2 = db.Column(db.Integer, nullable = False)
    aadhar_number = db.Column(db.Integer, nullable = False)
    center_id = db.Column(db.Integer, nullable = False)


    def __repr__(self):
        return '<Candidate %r>' % self.id

# class CandidateChild(db.Model):
#     id = db.Column(db.Integer, primary_key = True)
#     name = db.Column(db.String(200), nullable = False)
#     age = db.Column(db.Integer, nullable = False)
#     location = db.Column(db.String(200), nullable = False)
#     mobile_number = db.Column(db.Integer, nullable = False)
#     father_name = db.Column(db.String(200), nullable = True)
#     father_mobile = db.Column(db.Integer, nullable = True)
#     mother_name = db.Column(db.String(200), nullable = True)
#     mother_mobile = db.Column(db.Integer, nullable = True)
#     aadhar_number = db.Column(db.Integer, nullable = False)

#     def __repr__(self):
#         return '<CandidateChild %r>' % self.id

# class Admin(db.Model,UserMixin):
#     id = db.Column(db.Integer, primary_key = True)
#     type = db.Column(db.String(5), default = "Admin")
#     username = db.Column(db.String(20), nullable = False, unique = True)
#     password = db.Column(db.String(80), nullable = False)

class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key = True, unique = True)
    type = db.Column(db.String(5), nullable = False)
    username = db.Column(db.String(20), nullable = False, unique = True)
    password = db.Column(db.String(80), nullable = False)
    admission_count = db.Column(db.Integer, default=10)
    lastUpdate = db.Column(db.DateTime, default = datetime.utcnow().date())
    
class RegisterForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                'That username already exists. Please choose a different one.')


class LoginForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')

@app.route('/', methods=['POST','GET'])
def index():
    if request.method == 'POST':
        pass
    else:
        centers = Center.query.order_by(Center.registered_date).all()
        return render_template('index.html',centers = centers)

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@app.route('/userLogin', methods=['GET', 'POST'])
def userLogin():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data, type = "User").first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('home'))
    return render_template('userLogin.html', form=form)

@app.route('/adminLogin', methods=['GET', 'POST'])
def adminLogin():
    form = LoginForm()
    if form.validate_on_submit():
        admin = User.query.filter_by(username=form.username.data, type = "Admin").first()
        if admin:
            if bcrypt.check_password_hash(admin.password, form.password.data):
                print(admin)
                login_user(admin)
                return redirect(url_for('home'))
    return render_template('adminLogin.html', form=form)

@ app.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('register.html')

@ app.route('/userRegister', methods=['GET', 'POST'])
def userRegister():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password, type = "User", admission_count = 10)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('home'))

    return render_template('userRegister.html', form=form)

@ app.route('/adminRegister', methods=['GET', 'POST'])
def adminRegister():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_admin = User(username=form.username.data, password=hashed_password, type = "Admin")
        db.session.add(new_admin)
        db.session.commit()
        login_user(new_admin)
        return redirect(url_for('home'))

    return render_template('adminRegister.html', form=form)

@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    print(current_user.lastUpdate.date())
    print(datetime.utcnow().date())
    if current_user.type == 'User' and current_user.lastUpdate.date() != datetime.utcnow().date():
        new_user = User.query.get_or_404(current_user.id)
        new_user.lastUpdate = datetime.utcnow().date()
        new_user.admission_count = 10
        db.session.commit()
        login_user(new_user)
        
    query = Center.query
    hours_list = [row.working_hours for row in db.session.query(Center.working_hours).distinct()]
    locations_list = [row.location for row in db.session.query(Center.location).distinct()]
    if request.method == 'POST':
        working_hours = request.form['working_hours']
        location = request.form['location']
        if working_hours != "null" or location != "null":
            centers = query
            if working_hours != "null" and location != "null":
                centers = query.filter(Center.working_hours == working_hours,Center.location == location).all()
            elif working_hours != "null":
                centers = query.filter(Center.working_hours == working_hours).all()
            else:
                centers = query.filter(Center.location == location).all()
            return render_template('home.html', user = current_user, centers = centers, hours_list = hours_list, locations_list = locations_list)
    centers = query.order_by(Center.registered_date.desc()).all()
    return render_template('home.html', user = current_user, centers = centers, hours_list = hours_list, locations_list = locations_list)

@app.route('/centerRegister', methods=['GET','POST'])
@login_required
def centerRegister():
    if request.method == 'POST':
        print(request.form['hospital'])
        new_center = Center(hospital = request.form['hospital'], working_hours = request.form['working_hours'], location = request.form['location'])
        db.session.add(new_center)
        db.session.commit()
        return redirect(url_for('home'))
    else:
        return render_template('centerRegister.html', user = current_user)

@app.route('/modify/<int:id>', methods=['GET','POST'])
@login_required
def modify(id):
    center = Center.query.get_or_404(id)
    if request.method == 'POST':
        center.hospital = request.form['hospital']
        center.working_hours = request.form['working_hours']
        center.location = request.form['location']
        db.session.commit()
        return redirect(url_for('home'))
    else:
        return render_template('centerModify.html', form = center, user=current_user)

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    center = Center.query.get_or_404(id)
    db.session.delete(center)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/admission/center=<int:center_id>', methods=['GET','POST'])
@login_required
def admission(center_id):
    if current_user.admission_count == 0:
        return redirect(url_for('home'))
    if request.method == 'POST':
        candidate = Candidate(name = request.form['name'],age = request.form['age'],location = request.form['location'],mobile_number = int(request.form['mobile_number']),mobile_number_2 = int(request.form['mobile_number_2']),aadhar_number = int(request.form['aadhar_number']),center_id = center_id)
        user = User.query.get_or_404(current_user.id)
        user.admission_count = user.admission_count - 1
        db.session.add(candidate)
        db.session.commit()
        login_user(user)
        print(current_user.admission_count)
        return redirect(url_for('home'))
    else:
        return render_template('admission.html', user = current_user)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)