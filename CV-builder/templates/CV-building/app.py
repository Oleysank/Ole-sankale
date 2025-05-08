cat << 'EOF' > app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email
import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import pdfkit
import stripe
import io

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SESSION_TYPE'] = 'sqlalchemy'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/cv_builder.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}
app.config['SESSION_SQLALCHEMY'] = None  # Will set after db initialization

os.makedirs('instance', exist_ok=True)
db = SQLAlchemy(app)
app.config['SESSION_SQLALCHEMY'] = db  # Use the same SQLAlchemy instance for sessions
Session(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

stripe.api_key = 'your-stripe-secret-key'

class User(UserMixin, db.Model):
 id = db.Column(db.Integer, primary_key=True)
 email = db.Column(db.String(120), unique=True, nullable=False)
 password = db.Column(db.String(120), nullable=False)

class CVData(db.Model):
 id = db.Column(db.Integer, primary_key=True)
 user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
 section = db.Column(db.String(50), nullable=False)
 data = db.Column(db.Text, nullable=False)

@login_manager.user_loader
def load_user(user_id):
 return User.query.get(int(user_id))

class RegisterForm(FlaskForm):
 email = StringField('Email', validators=[DataRequired(), Email()])
 password = PasswordField('Password', validators=[DataRequired()])
 submit = SubmitField('Register')

class LoginForm(FlaskForm):
 email = StringField('Email', validators=[DataRequired(), Email()])
 password = PasswordField('Password', validators=[DataRequired()])
 submit = SubmitField('Login')

def allowed_file(filename):
 return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
 if current_user.is_authenticated:
     return redirect(url_for('personal_info'))
 return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
 form = RegisterForm()
 if form.validate_on_submit():
     if User.query.filter_by(email=form.email.data).first():
         flash('Email already registered.', 'error')
         return redirect(url_for('register'))
     hashed_password = generate_password_hash(form.password.data)
     new_user = User(email=form.email.data, password=hashed_password)
     db.session.add(new_user)
     db.session.commit()
     flash('Registration successful! Please log in.', 'success')
     return redirect(url_for('login'))
 return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
 form = LoginForm()
 if form.validate_on_submit():
     user = User.query.filter_by(email=form.email.data).first()
     if user and check_password_hash(user.password, form.password.data):
         login_user(user)
         return redirect(url_for('personal_info'))
     flash('Invalid email or password.', 'error')
 return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
 logout_user()
 return redirect(url_for('login'))

@app.route('/personal_info', methods=['GET', 'POST'])
@login_required
def personal_info():
 if request.method == 'POST':
     data = {
         'first_name': request.form.get('first_name'),
         'last_name': request.form.get('last_name'),
         'email': request.form.get('email'),
         'phone': request.form.get('phone'),
         'address': request.form.get('address')
     }
     cv_data = CVData(user_id=current_user.id, section='personal_info', data=str(data))
     db.session.add(cv_data)
     db.session.commit()
     flash('Personal information saved!', 'success')
     return redirect(url_for('education'))
 return render_template('personal_info.html')

@app.route('/education', methods=['GET', 'POST'])
@login_required
def education():
 if request.method == 'POST':
     data = {
         'institution': request.form.get('institution'),
         'degree': request.form.get('degree'),
         'start_date': request.form.get('start_date'),
         'end_date': request.form.get('end_date')
     }
     cv_data = CVData(user_id=current_user.id, section='education', data=str(data))
     db.session.add(cv_data)
     db.session.commit()
     flash('Education saved!', 'success')
     return redirect(url_for('experience'))
 return render_template('education.html')

@app.route('/experience', methods=['GET', 'POST'])
@login_required
def experience():
 if request.method == 'POST':
     data = {
         'company': request.form.get('company'),
         'position': request.form.get('position'),
         'start_date': request.form.get('start_date'),
         'end_date': request.form.get('end_date'),
         'description': request.form.get('description')
     }
     cv_data = CVData(user_id=current_user.id, section='experience', data=str(data))
     db.session.add(cv_data)
     db.session.commit()
     flash('Experience saved!', 'success')
     return redirect(url_for('skills'))
 return render_template('experience.html')

@app.route('/skills', methods=['GET', 'POST'])
@login_required
def skills():
 if request.method == 'POST':
     data = {'skill': request.form.get('skill')}
     cv_data = CVData(user_id=current_user.id, section='skills', data=str(data))
     db.session.add(cv_data)
     db.session.commit()
     flash('Skill saved!', 'success')
     return redirect(url_for('certifications'))
 return render_template('skills.html')

@app.route('/certifications', methods=['GET', 'POST'])
@login_required
def certifications():
 if request.method == 'POST':
     data = {
         'certification': request.form.get('certification'),
         'issuer': request.form.get('issuer'),
         'date': request.form.get('date')
     }
     cv_data = CVData(user_id=current_user.id, section='certifications', data=str(data))
     db.session.add(cv_data)
     db.session.commit()
     flash('Certification saved!', 'success')
     return redirect(url_for('referees'))
 return render_template('certifications.html')

@app.route('/referees', methods=['GET', 'POST'])
@login_required
def referees():
 if request.method == 'POST':
     data = {
         'name': request.form.get('name'),
         'contact': request.form.get('contact'),
         'relationship': request.form.get('relationship')
     }
     cv_data = CVData(user_id=current_user.id, section='referees', data=str(data))
     db.session.add(cv_data)
     db.session.commit()
     flash('Referee saved!', 'success')
     return redirect(url_for('languages'))
 return render_template('referees.html')

@app.route('/languages', methods=['GET', 'POST'])
@login_required
def languages():
 if request.method == 'POST':
     data = {
         'language': request.form.get('language'),
         'proficiency': request.form.get('proficiency')
     }
     cv_data = CVData(user_id=current_user.id, section='languages', data=str(data))
     db.session.add(cv_data)
     db.session.commit()
     flash('Language saved!', 'success')
     return redirect(url_for('hobbies'))
 languages = CVData.query.filter_by(user_id=current_user.id, section='languages').all()
 return render_template('languages.html', languages=languages)

@app.route('/hobbies', methods=['GET', 'POST'])
@login_required
def hobbies():
 if request.method == 'POST':
     data = {'hobby': request.form.get('hobby')}
     cv_data = CVData(user_id=current_user.id, section='hobbies', data=str(data))
     db.session.add(cv_data)
     db.session.commit()
     flash('Hobby saved!', 'success')
     return redirect(url_for('summary'))
 return render_template('hobbies.html')

@app.route('/summary', methods=['GET', 'POST'])
@login_required
def summary():
 if request.method == 'POST':
     data = {'summary': request.form.get('summary')}
     cv_data = CVData(user_id=current_user.id, section='summary', data=str(data))
     db.session.add(cv_data)
     db.session.commit()
     flash('Summary saved!', 'success')
     return redirect(url_for('choose_template'))
 return render_template('summary.html')

@app.route('/choose_template', methods=['GET', 'POST'])
@login_required
def choose_template():
 if request.method == 'POST':
     session['template'] = request.form.get('template')
     return redirect(url_for('preview'))
 return render_template('choose_template.html')

@app.route('/preview')
@login_required
def preview():
 cv_data = CVData.query.filter_by(user_id=current_user.id).all()
 template = session.get('template', 'cv_classic.html')
 return render_template(template, cv_data=cv_data)

@app.route('/keyword_suggestion', methods=['GET', 'POST'])
@login_required
def keyword_suggestion():
 if request.method == 'POST':
     job_description = request.form.get('job_description')
     keywords = set(job_description.lower().split())  # Simple keyword extraction
     flash(f'Suggested keywords: {", ".join(keywords)}', 'success')
     return redirect(url_for('keyword_suggestion'))
 return render_template('keyword_suggestion.html')

@app.route('/generate_pdf')
@login_required
def generate_pdf():
 cv_data = CVData.query.filter_by(user_id=current_user.id).all()
 template = session.get('template', 'cv_classic.html')
 rendered = render_template(template, cv_data=cv_data)
 pdf = pdfkit.from_string(rendered, False)
 return send_file(
     io.BytesIO(pdf),
     mimetype='application/pdf',
     as_attachment=True,
     download_name='cv.pdf'
 )

@app.route('/pricing')
def pricing():
 return render_template('pricing.html')

@app.route('/create_checkout_session', methods=['POST'])
@login_required
def create_checkout_session():
 try:
     checkout_session = stripe.checkout.Session.create(
         payment_method_types=['card'],
         line_items=[{
             'price_data': {
                 'currency': 'usd',
                 'product_data': {'name': 'CV Builder Premium'},
                 'unit_amount': 999,
             },
             'quantity': 1,
         }],
         mode='payment',
         success_url=url_for('preview_success', _external=True),
         cancel_url=url_for('pricing', _external=True),
     )
     return redirect(checkout_session.url, code=303)
 except Exception as e:
     flash(str(e), 'error')
     return redirect(url_for('pricing'))

@app.route('/preview_success')
@login_required
def preview_success():
 return render_template('preview_success.html')

@app.route('/upload_photo', methods=['POST'])
@login_required
def upload_photo():
 if 'photo' not in request.files:
     flash('No file part', 'error')
     return redirect(url_for('personal_info'))
 file = request.files['photo']
 if file.filename == '':
     flash('No selected file', 'error')
     return redirect(url_for('personal_info'))
 if file and allowed_file(file.filename):
     filename = secure_filename(file.filename)
     file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
     flash('Photo uploaded successfully!', 'success')
     return redirect(url_for('personal_info'))
 flash('Invalid file type', 'error')
 return redirect(url_for('personal_info'))

if __name__ == '__main__':
 with app.app_context():
     db.create_all()
 app.run(debug=True)
EOF