# CV Builder Application

A Flask-based web application for building and generating professional CVs in PDF format.

## Prerequisites
- Python 3.12.1
- wkhtmltopdf (`sudo apt-get install wkhtmltopdf`)
- Git

## Setup Instructions
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Oleysank/Ole-sankale.git
   cd Ole-sankale/CV-builder/templates/CV-building
   ```

2. **Create a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scriptsctivate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Environment Variables**:
   ```bash
   export XDG_RUNTIME_DIR=/tmp/runtime-codespace
   ```

5. **Run the Application**:
   ```bash
   python app.py
   ```
   - Open `http://127.0.0.1:5000` in your browser.

## Project Structure
- `app.py`: Main Flask application with user authentication and payment integration.
- `templates/`: HTML templates (e.g., `cv_classic.html`, `preview.html`, `login.html`).
- `static/css/style.css`: CSS styles.
- `sessions.db`: SQLite database for session storage.
- `cv_builder.db`: SQLite database for user accounts.

## Notes
- Ensure `wkhtmltopdf` is installed at `/usr/bin/wkhtmltopdf`.
- Uses SQLite for session management and user data.
- For production, deploy with Gunicorn and configure HTTPS.
- Payment integration requires Stripe setup.
