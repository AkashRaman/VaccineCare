from flask import Flask, render_template, url_for, request, redirect
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField,EmailField,IntegerField
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

class Centre(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    hospital = db.Column(db.String(200), nullable = False)
    working_hours = db.Column(db.String(200), nullable = False)
    location = db.Column(db.String(200), nullable = False)
    registered_date = db.Column(db.DateTime, default = datetime.utcnow)
    dosages = db.Column(db.String(200),nullable = False)

    def __repr__(self):
        return '<Centres %r>' % self.id 

class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(200), nullable = False)
    age = db.Column(db.Integer, nullable = False)
    location = db.Column(db.String(200), nullable = False)
    mobile_number = db.Column(db.Integer, nullable = False)
    mobile_number_2 = db.Column(db.Integer, nullable = False)
    aadhar_number = db.Column(db.Integer, nullable = False)
    centre_id = db.Column(db.Integer, nullable = False)
    dosage = db.Column(db.String(200),nullable = False)

    def __repr__(self):
        return '<Candidate %r>' % self.id

class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key = True, unique = True)
    type = db.Column(db.String(5), nullable = False)
    email = db.Column(db.String(40), nullable = False, unique = True)
    password = db.Column(db.String(80), nullable = False)
    username = db.Column(db.String(30), nullable = False)
    age = db.Column(db.Integer, nullable = False)
    mobile_number = db.Column(db.Integer, nullable = False)
    backup_email = db.Column(db.String(40), nullable = False)
    admission_count = db.Column(db.Integer, default=10)
    lastUpdate = db.Column(db.DateTime, default = datetime.utcnow().date())
    
class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    email = EmailField(validators=[InputRequired()], render_kw={"placeholder":"Email"})

    backup_email = EmailField(validators=[InputRequired()], render_kw={"placeholder":"Backup Email"})

    age = IntegerField(validators=[InputRequired()], render_kw={"placeholder": "Age"})

    mobile_number = StringField(validators=[InputRequired(),Length(min=10, max=10)], render_kw={"placeholder": "Mobile Number"})  

    submit = SubmitField('Register')

    def validate_email(self, email):
        existing_user_email = User.query.filter_by(email=email.data).first()
        if existing_user_email:
            raise ValidationError('That username already exists. Please choose a different one.')


class LoginForm(FlaskForm):

    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    email = EmailField(validators=[InputRequired()], render_kw={"placeholder":"Email"})

    submit = SubmitField('Login')

@app.route('/', methods=['POST','GET'])
def index():
    if request.method == 'POST':
        pass
    else:
        centres = Centre.query.order_by(Centre.registered_date).all()
        return render_template('index.html',centres = centres)

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@app.route('/userLogin', methods=['GET', 'POST'])
def userLogin():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data, type = "User").first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('home'))
    else:
        print(form.errors)
    return render_template('userLogin.html', form=form)

@app.route('/adminLogin', methods=['GET', 'POST'])
def adminLogin():
    form = LoginForm()
    if form.validate_on_submit():
        admin = User.query.filter_by(email=form.email.data, type = "Admin").first()
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
    errorMsg = ""
    if form.validate_on_submit():
        name = "".join(form.username.data.split())
        if name.isalpha() == False:
            errorMsg = "Please entre a valid name"
        elif form.email.data == form.backup_email.data:
            errorMsg = "Do not entre same email as backup email"
        elif form.mobile_number.data.isdigit() == False:
            errorMsg = "Please entre a valid mobile number"
        if errorMsg == "":
            hashed_password = bcrypt.generate_password_hash(form.password.data)
            new_user = User(email=form.email.data, password=hashed_password,username = form.username.data,backup_email = form.backup_email.data,age = form.age.data,mobile_number = form.mobile_number.data, type = "User", admission_count = 10)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('home'))

    return render_template('userRegister.html', form=form, errorMsg = errorMsg)

@ app.route('/adminRegister', methods=['GET', 'POST'])
def adminRegister():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_admin = User(email=form.email.data, password=hashed_password,username = form.username.data, backup_email = form.backup_email.data,age = form.age.data,mobile_number = form.mobile_number.data, type = "Admin")
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
        
    query = Centre.query
    hours_list = [row.working_hours for row in db.session.query(Centre.working_hours).distinct()]
    locations_list = [row.location for row in db.session.query(Centre.location).distinct()]
    dosages_list = []
    for dosages in [row.dosages.split(", ") for row in db.session.query(Centre.dosages).distinct()]:
        for dosage in dosages:
            if dosages_list == [] or int(dosage[1:len(dosage) - 1]) not in dosages_list:
                dosages_list.append(int(dosage[1:len(dosage) - 1]))
    dosages_list.sort()
    centres = query.order_by(Centre.registered_date.desc()).all()
    if request.method == 'POST':
        working_hours = request.form['working_hours']
        location = request.form['location']
        dosage = request.form['dosage']
        if working_hours != "null" or location != "null" or dosage != "null":
            if working_hours != "null" and location != "null" and dosage != "null":
                centres = query.filter(Centre.working_hours == working_hours,Centre.location == location, Centre.dosages.contains("|" + dosage + "|")).order_by(Centre.registered_date.desc()).all()
            elif working_hours != "null" and location != "null":
                centres = query.filter(Centre.working_hours == working_hours,Centre.location == location).order_by(Centre.registered_date.desc()).all()
            elif working_hours != "null" and dosage != "null":
                centres = query.filter(Centre.working_hours == working_hours,Centre.dosages.contains("|" + dosage + "|")).order_by(Centre.registered_date.desc()).all()
            elif location != "null" and dosage != "null":
                centres = query.filter(Centre.location == location,Centre.dosages.contains("|" + dosage + "|")).order_by(Centre.registered_date.desc()).all()
            elif working_hours != "null":
                centres = query.filter(Centre.working_hours == working_hours).order_by(Centre.registered_date.desc()).all()
            elif location != "null":
                centres = query.filter(Centre.location == location).order_by(Centre.registered_date.desc()).all()
            else:
                centres = query.filter(Centre.dosages.contains("|" + dosage + "|")).order_by(Centre.registered_date.desc()).all()
    return render_template('home.html', user = current_user, centres = centres, hours_list = hours_list, locations_list = locations_list, dosages_list = dosages_list)

@app.route('/centerRegister', methods=['GET','POST'])
@login_required
def centerRegister():
    if request.method == 'POST':
        arr = []
        for i in range(int(request.form['dosage_no'])):
            string = "dosage_" + str(i+1)
            arr.append("|" + request.form[string] + "|")
        dosages = ", ".join(arr)
        if comapareTime(request.form['from_hour'],request.form['to_hour']):
            working_hours = request.form['from_hour'] + " - " +request.form['to_hour']
            new_centre = Centre(hospital = request.form['hospital'], working_hours = working_hours, location = request.form['location'], dosages=dosages)
            print(dosages)
            db.session.add(new_centre)
            db.session.commit()
            return redirect(url_for('home'))
    return render_template('centerRegister.html', user = current_user)

def comapareTime(from_hour,to_hour):
    from_time = int(from_hour[:2]) * 100 + int(from_hour[3:])
    to_time = int(to_hour[:2]) * 100 + int(to_hour[3:])
    return from_time < to_time

@app.route('/modify/<int:id>', methods=['GET','POST'])
@login_required
def modify(id):
    centre = Centre.query.get_or_404(id)
    if request.method == 'POST':
        arr = []
        for i in range(int(request.form['dosage_no'])):
            string = "dosage_" + str(i+1)
            arr.append(request.form[string])
        dosages = ", ".join(arr)
        centre.hospital = request.form['hospital']
        centre.working_hours = request.form['working_hours']
        centre.location = request.form['location']
        centre.dosages = dosages
        db.session.commit()
        return redirect(url_for('home'))
    else:
        dosages = centre.dosages.split(", ")
        return render_template('centerModify.html', form = centre, user=current_user, dosages = dosages)

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    centre = Centre.query.get_or_404(id)
    db.session.delete(centre)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/admission/centre=<int:centre_id>', methods=['GET','POST'])
@login_required
def admission(centre_id):
    if current_user.admission_count == 0:
        return redirect(url_for('home'))
    if request.method == 'POST':
        candidate = Candidate(name = request.form['name'],age = request.form['age'],location = request.form['location'],mobile_number = int(request.form['mobile_number']),mobile_number_2 = int(request.form['mobile_number_2']),aadhar_number = int(request.form['aadhar_number']),centre_id = centre_id)
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