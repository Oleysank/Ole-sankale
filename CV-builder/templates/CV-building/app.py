from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Required for using flash messages

# Configure upload folder
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create the upload directory if it doesn't exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Home route - redirects to the personal_info page
@app.route('/')
def home():
    return redirect(url_for('personal_info'))

# Route for Personal Information page
@app.route('/personal_info', methods=['GET', 'POST'])
def personal_info():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        photo = request.files.get('photo')
        
        # Validate required fields
        if not all([name, email, phone, photo]):
            flash('Error: All fields are required.', 'error')
            return redirect(url_for('personal_info'))
        
        # Validate file type
        if photo and photo.filename:
            if not photo.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                flash('Error: Only PNG and JPG files are allowed.', 'error')
                return redirect(url_for('personal_info'))
            filename = secure_filename(photo.filename)
            try:
                photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            except Exception as e:
                flash(f'Error saving photo: {str(e)}', 'error')
                return redirect(url_for('personal_info'))
        else:
            flash('Error: Photo is required.', 'error')
            return redirect(url_for('personal_info'))
        
        # Store data in session
        session['name'] = name
        session['email'] = email
        session['phone'] = phone
        session['photo'] = filename
        
        flash('Personal Information saved! Proceed to the next section.')
        return redirect(url_for('summary'))
    return render_template('personal_info.html')

# Route for Professional Summary page
@app.route('/summary', methods=['GET', 'POST'])
def summary():
    if request.method == 'POST':
        print("Form data:", request.form)  # Debug: Print form data
        summary_text = request.form.get('summary')
        if not summary_text:
            flash('Error: Professional Summary is required.', 'error')
            return redirect(url_for('summary'))
        
        # Store it in the session
        session['summary'] = summary_text
        
        flash('Professional Summary saved! Proceed to the next section.')
        return redirect(url_for('education'))
    return render_template('Summary.html')

# Route for Education page
@app.route('/education', methods=['GET', 'POST'])
def education():
    if request.method == 'POST':
        # Get form data for education
        institution = request.form.get('institution')
        degree = request.form.get('degree')
        field_of_study = request.form.get('field_of_study')
        graduation_date = request.form.get('graduation_date')
        
        # Validate required fields
        if not all([institution, degree, field_of_study, graduation_date]):
            flash('Error: All education fields are required.', 'error')
            return redirect(url_for('education'))
        
        # Store it in the session
        session['institution'] = institution
        session['degree'] = degree
        session['field_of_study'] = field_of_study
        session['graduation_date'] = graduation_date
        
        flash('Education details saved! Proceed to the next section.')
        return redirect(url_for('experience'))
    return render_template('Education.html')

# Route for Experience page
@app.route('/experience', methods=['GET', 'POST'])
def experience():
    if request.method == 'POST':
        # Get form data for experience
        job_title = request.form.get('job_title')
        employer = request.form.get('employer')
        job_location = request.form.get('job_location')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        responsibilities = request.form.get('responsibilities')
        
        # Validate required fields
        if not all([job_title, employer, job_location, start_date, end_date, responsibilities]):
            flash('Error: All experience fields are required.', 'error')
            return redirect(url_for('experience'))
        
        # Store it in the session
        session['job_title'] = job_title
        session['employer'] = employer
        session['job_location'] = job_location
        session['start_date'] = start_date
        session['end_date'] = end_date
        session['responsibilities'] = responsibilities
        
        flash('Work Experience saved! Proceed to the next section.')
        return redirect(url_for('skills'))
    return render_template('Experience.html')

# Route for Skills page
@app.route('/skills', methods=['GET', 'POST'])
def skills():
    if request.method == 'POST':
        # Get form data for skills
        skills = request.form.get('skills')
        
        # Validate required field
        if not skills:
            flash('Error: Skills field is required.', 'error')
            return redirect(url_for('skills'))
        
        # Store it in the session
        session['skills'] = skills
        
        flash('Skills saved! Proceed to the next section.')
        return redirect(url_for('referees'))
    return render_template('Skills.html')

# Route for Referees page
@app.route('/referees', methods=['GET', 'POST'])
def referees():
    if request.method == 'POST':
        # Get form data for referees
        referee_name = request.form.get('referee_name')
        referee_contact = request.form.get('referee_contact')
        
        # Validate required fields
        if not all([referee_name, referee_contact]):
            flash('Error: All referee fields are required.', 'error')
            return redirect(url_for('referees'))
        
        # Store it in the session
        session['referee_name'] = referee_name
        session['referee_contact'] = referee_contact
        
        flash('Referees saved! Proceed to the next section.')
        return redirect(url_for('preview'))
    return render_template('Referees.html')

# Route for Preview page (final CV preview)
@app.route('/preview', methods=['GET', 'POST'])
def preview():
    if request.method == 'POST':
        flash('Your CV has been generated successfully!')
        return redirect(url_for('preview_success'))
    
    # Pass session data to the template for preview
    cv_data = {
        'name': session.get('name'),
        'email': session.get('email'),
        'phone': session.get('phone'),
        'photo': session.get('photo'),
        'summary': session.get('summary'),
        'institution': session.get('institution'),
        'degree': session.get('degree'),
        'field_of_study': session.get('field_of_study'),
        'graduation_date': session.get('graduation_date'),
        'job_title': session.get('job_title'),
        'employer': session.get('employer'),
        'job_location': session.get('job_location'),
        'start_date': session.get('start_date'),
        'end_date': session.get('end_date'),
        'responsibilities': session.get('responsibilities'),
        'skills': session.get('skills'),
        'referee_name': session.get('referee_name'),
        'referee_contact': session.get('referee_contact'),
    }
    return render_template('Preview.html', cv=cv_data)

# Route for success page (final confirmation)
@app.route('/preview_success', methods=['GET'])
def preview_success():
    return render_template('Preview_success.html')

# Final route to generate the CV and possibly download it
@app.route('/generate', methods=['POST'])
def generate():
    flash('Thank you Mandela Pulei, We have received your message')
    return redirect(url_for('preview_success'))

if __name__ == '__main__':
    app.run(debug=True)
