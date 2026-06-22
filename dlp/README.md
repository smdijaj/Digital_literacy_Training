# Digital Literacy Training Program (CSP)

A Flask + HTML/CSS/JS + SQLite web app for a Community Service Project.

## Run locally
```bash
pip install -r requirements.txt
python app.py
```
Open http://localhost:5000

## Deploy on Render.com
1. Push this folder to a GitHub repo.
2. On Render → **New Web Service** → connect repo.
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn app:app`
5. Done — your live URL will appear.

## Structure
```
app.py                 Flask backend + routes + SQLite
templates/             Jinja2 HTML templates
static/css/style.css   Styling
static/js/main.js      Interactivity
database.db            Auto-created on first run
requirements.txt       Python dependencies
Procfile               For Render / Heroku
```
