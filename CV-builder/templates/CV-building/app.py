from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from flask_session import Session
import os
from werkzeug.utils import secure_filename
from io import BytesIO
import pdfkit
import tempfile
import logging
import urllib.parse

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Configure Flask-Session with SQLite
app.config['SESSION_TYPE'] = 'sqlalchemy'
app.config['SESSION_SQLALCHEMY_TABLE'] = 'sessions'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sessions.db'
Session(app)

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def home():
    session.clear()
    return redirect(url_for('personal_info'))

@app.route('/personal_info', methods=['GET', 'POST'])
def personal_info():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        linkedin = request.form.get('linkedin')
        if not all([name, email]):
            flash('Name and email are required.', 'error')
            return redirect(url_for('personal_info'))
        session['personal_info'] = {
            'name': name,
            'email': email,
            'phone': phone or '',
            'linkedin': linkedin or ''
        }
        session['summary'] = ''
        session['education'] = []
        session['experience'] = []
        session['skills'] = []
        session['tech_skills'] = {'python': [], 'r': [], 'sql': []}
        session['hobbies'] = []
        session['certifications'] = []
        session['referees'] = []
        logger.debug(f"Personal Info saved: {session['personal_info']}")
        flash('Personal Info saved! Proceed to Summary.')
        return redirect(url_for('summary'))
    return render_template('personal_info.html')

@app.route('/summary', methods=['GET', 'POST'])
def summary():
    if request.method == 'POST':
        summary = request.form.get('summary')
        if not summary:
            flash('Summary is required.', 'error')
            return redirect(url_for('summary'))
        session['summary'] = summary
        logger.debug(f"Summary saved: {session['summary']}")
        flash('Summary saved! Proceed to Education.')
        return redirect(url_for('education'))
    return render_template('summary.html')

@app.route('/education', methods=['GET', 'POST'])
def education():
    if request.method == 'POST':
        institution = request.form.get('institution')
        degree = request.form.get('degree')
        field = request.form.get('field')
        grad_date = request.form.get('grad_date')
        if not all([institution, degree, field, grad_date]):
            flash('All education fields are required.', 'error')
            return redirect(url_for('education'))
        if len(session.get('education', [])) >= 5:
            flash('Maximum 5 education entries allowed.', 'error')
            return redirect(url_for('education'))
        entry = {'institution': institution, 'degree': degree, 'field': field, 'grad_date': grad_date}
        session['education'].append(entry)
        session.modified = True
        logger.debug(f"Education saved: {session['education']}")
        flash('Education saved! Add more or proceed.')
        return redirect(url_for('education'))
    return render_template('education.html', education=session.get('education', []))

@app.route('/experience', methods=['GET', 'POST'])
def experience():
    if request.method == 'POST':
        title = request.form.get('title')
        employer = request.form.get('employer')
        location = request.form.get('location')
        start = request.form.get('start')
        end = request.form.get('end')
        duties = request.form.get('duties')
        if not all([title, employer, location, start, end, duties]):
            flash('All experience fields are required.', 'error')
            return redirect(url_for('experience'))
        if len(session.get('experience', [])) >= 5:
            flash('Maximum 5 experience entries allowed.', 'error')
            return redirect(url_for('experience'))
        entry = {'title': title, 'employer': employer, 'location': location, 'start': start, 'end': end, 'duties': duties}
        session['experience'].append(entry)
        session.modified = True
        logger.debug(f"Experience saved: {session['experience']}")
        flash('Experience saved! Add more or proceed.')
        return redirect(url_for('experience'))
    return render_template('experience.html', experience=session.get('experience', []))

@app.route('/skills', methods=['GET', 'POST'])
def skills():
    if request.method == 'POST':
        language = request.form.get('language')
        library = request.form.get('library')
        if language and library:
            if language.lower() not in session['tech_skills']:
                flash('Invalid language selected.', 'error')
                return redirect(url_for('skills'))
            if len(session['tech_skills'][language.lower()]) >= 5:
                flash(f'Maximum 5 {language} libraries allowed.', 'error')
                return redirect(url_for('skills'))
            session['tech_skills'][language.lower()].append(library)
            session.modified = True
            logger.debug(f"Tech Skills saved: {session['tech_skills']}")
            flash(f'{library} added to {language} skills! Add more or proceed.')
            return redirect(url_for('skills'))
        skill = request.form.get('skill')
        description = request.form.get('description')
        if skill:
            if len(session.get('skills', [])) >= 5:
                flash('Maximum 5 skills allowed.', 'error')
                return redirect(url_for('skills'))
            entry = {'name': skill, 'description': description or ''}
            session['skills'].append(entry)
            session.modified = True
            logger.debug(f"Skills saved: {session['skills']}")
            flash(f'{skill} saved! Add more or proceed.')
            return redirect(url_for('skills'))
    return render_template('skills.html', skills=session.get('skills', []), tech_skills=session.get('tech_skills', {'python': [], 'r': [], 'sql': []}))

@app.route('/hobbies', methods=['GET', 'POST'])
def hobbies():
    if request.method == 'POST':
        hobby = request.form.get('hobby')
        description = request.form.get('description')
        if not hobby:
            flash('Hobby is required.', 'error')
            return redirect(url_for('hobbies'))
        if len(session.get('hobbies', [])) >= 5:
            flash('Maximum 5 hobbies allowed.', 'error')
            return redirect(url_for('hobbies'))
        entry = {'name': hobby, 'description': description or ''}
        session['hobbies'].append(entry)
        session.modified = True
        logger.debug(f"Hobbies saved: {session['hobbies']}")
        flash(f'{hobby} saved! Add more or proceed.')
        return redirect(url_for('hobbies'))
    return render_template('hobbies.html', hobbies=session.get('hobbies', []))

@app.route('/certifications', methods=['GET', 'POST'])
def certifications():
    if request.method == 'POST':
        title = request.form.get('title')
        issuer = request.form.get('issuer')
        date = request.form.get('date')
        description = request.form.get('description')
        verification_code = request.form.get('verification_code')
        if not all([title, issuer, date]):
            flash('Title, issuer, and date are required.', 'error')
            return redirect(url_for('certifications'))
        if len(session.get('certifications', [])) >= 5:
            flash('Maximum 5 certifications allowed.', 'error')
            return redirect(url_for('certifications'))
        entry = {
            'title': title,
            'issuer': issuer,
            'date': date,
            'description': description or '',
            'verification_code': verification_code or ''
        }
        if 'certifications' not in session:
            session['certifications'] = []
        session['certifications'].append(entry)
        session.modified = True
        logger.debug(f"Certifications saved: {session['certifications']}")
        flash(f'{title} saved! Add more or proceed.')
        return redirect(url_for('certifications'))
    logger.debug(f"Current certifications: {session.get('certifications', [])}")
    return render_template('certifications.html', certifications=session.get('certifications', []))

@app.route('/referees', methods=['GET', 'POST'])
def referees():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        position = request.form.get('position')
        organization = request.form.get('organization')
        if not all([name, email]):
            flash('Name and email are required.', 'error')
            return redirect(url_for('referees'))
        if len(session.get('referees', [])) >= 5:
            flash('Maximum 5 referees allowed.', 'error')
            return redirect(url_for('referees'))
        entry = {
            'name': name,
            'email': email,
            'phone': phone or '',
            'position': position or '',
            'organization': organization or ''
        }
        session['referees'].append(entry)
        session.modified = True
        logger.debug(f"Referees saved: {session['referees']}")
        flash('Referee saved! Add more or proceed.')
        return redirect(url_for('referees'))
    logger.debug(f"Current referees: {session.get('referees', [])}")
    return render_template('referees.html', referees=session.get('referees', []))

@app.route('/preview')
def preview():
    cv_data = {
        'name': session.get('personal_info', {}).get('name', ''),
        'email': session.get('personal_info', {}).get('email', ''),
        'phone': session.get('personal_info', {}).get('phone', ''),
        'linkedin': session.get('personal_info', {}).get('linkedin', ''),
        'summary': session.get('summary', ''),
        'education': session.get('education', []),
        'experience': session.get('experience', []),
        'skills': session.get('skills', []),
        'tech_skills': session.get('tech_skills', {'python': [], 'r': [], 'sql': []}),
        'hobbies': session.get('hobbies', []),
        'certifications': session.get('certifications', []),
        'referees': session.get('referees', [])
    }
    logger.debug(f"Preview CV data: {cv_data}")
    return render_template('preview.html', cv=cv_data)

@app.route('/choose_template', methods=['GET', 'POST'])
def choose_template():
    if request.method == 'POST':
        template = request.form.get('template')
        session['template_choice'] = template
        return redirect(url_for('preview_success'))
    return render_template('choose_template.html')

@app.route('/preview_success', methods=['GET', 'POST'])
def preview_success():
    if request.method == 'POST':
        template_choice = session.get('template_choice', 'classic')
        template_map = {
            'classic': 'cv_classic.html',
            'modern': 'cv_modern.html',
            'minimalist': 'cv_minimal.html'
        }
        template_file = template_map.get(template_choice, 'cv_classic.html')
        
        cv_data = {
            'name': session.get('personal_info', {}).get('name', ''),
            'email': session.get('personal_info', {}).get('email', ''),
            'phone': session.get('personal_info', {}).get('phone', ''),
            'linkedin': session.get('personal_info', {}).get('linkedin', ''),
            'summary': session.get('summary', ''),
            'education': session.get('education', []),
            'experience': session.get('experience', []),
            'skills': session.get('skills', []),
            'tech_skills': session.get('tech_skills', {'python': [], 'r': [], 'sql': []}),
            'hobbies': session.get('hobbies', []),
            'certifications': session.get('certifications', []),
            'referees': session.get('referees', [])
        }
        logger.debug(f"Preview success CV data: {cv_data}")

        # Render HTML with absolute paths for static assets
        static_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'static'))
        cv_data['static_base'] = f'file://{urllib.parse.quote(static_path)}/'
        html = render_template(template_file, cv=cv_data)

        # Save HTML to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as temp_html:
            temp_html.write(html.encode('utf-8'))
            temp_html_path = temp_html.name

        # Generate PDF with wkhtmltopdf
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            config = pdfkit.configuration(wkhtmltopdf='/usr/bin/wkhtmltopdf')
            pdfkit.from_file(temp_html_path, temp_file.name, configuration=config, options={
                'page-size': 'Letter',
                'enable-local-file-access': '',
                'encoding': 'UTF-8'
            })
            temp_file_path = temp_file.name
        
        # Clean up temporary HTML file
        os.unlink(temp_html_path)

        # Send PDF
        with open(temp_file_path, 'rb') as f:
            buffer = BytesIO(f.read())
        os.unlink(temp_file_path)
        
        buffer.seek(0)
        return send_file(buffer, as_attachment=True, download_name=f"{session.get('personal_info', {}).get('name', 'cv')}_cv.pdf", mimetype='application/pdf')
    return render_template('preview_success.html')

@app.route('/new_cv')
def new_cv():
    session.clear()
    flash('Started a new CV! Please enter your personal information.')
    return redirect(url_for('personal_info'))

if __name__ == '__main__':
    app.run(debug=True)