from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3, os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dlp-csp-secret-change-me")
DB = os.path.join(os.path.dirname(__file__), "database.db")

# ---------- Database ----------
def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    con = db(); c = con.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS contacts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, email TEXT, message TEXT,
        created_at TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS quiz_results(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, score INTEGER, total INTEGER, passed INTEGER,
        created_at TEXT)""")
    con.commit(); con.close()

# ---------- Content ----------
MODULES = [
    {"id":"internet","icon":"🌐","title":"Internet Basics",
     "desc":"Understand how the internet works, browsers, search engines, and safe browsing.",
     "points":["What is the Internet & World Wide Web","Using browsers: Chrome, Edge, Firefox",
              "Effective searching on Google","Recognizing secure (HTTPS) websites","Bookmarks, downloads & history"]},
    {"id":"email","icon":"✉️","title":"Email Communication",
     "desc":"Create, send, and manage emails professionally and safely.",
     "points":["Creating an email account","Composing, replying & forwarding",
              "Attachments & inbox organization","Spam, phishing & junk filters","Email etiquette"]},
    {"id":"cyber","icon":"🛡️","title":"Online Safety & Cyber Security",
     "desc":"Protect your identity, data, and devices from online threats.",
     "points":["Strong passwords & 2-factor auth","Identifying phishing & scams",
              "Safe Wi-Fi & VPN basics","Antivirus & software updates","Privacy on social platforms"]},
    {"id":"upi","icon":"💳","title":"Digital Payments (UPI & Banking)",
     "desc":"Learn UPI, mobile banking, and how to transact securely online.",
     "points":["UPI apps: GPay, PhonePe, Paytm, BHIM","Setting up a UPI PIN safely",
              "QR code payments","Internet & mobile banking basics","Avoiding payment frauds"]},
    {"id":"social","icon":"📱","title":"Social Media Awareness",
     "desc":"Use social media responsibly while protecting privacy and well-being.",
     "points":["Privacy & visibility settings","Recognizing fake news",
              "Digital footprint & reputation","Cyberbullying — what to do","Healthy screen-time habits"]},
    {"id":"gov","icon":"🏛️","title":"Government Digital Services",
     "desc":"Access government schemes and services online with confidence.",
     "points":["DigiLocker & Aadhaar services","UMANG app for government services",
              "Online PAN, passport & ration card","Income tax e-filing basics","Public grievance portals"]},
]

QUIZ = [
    {"q":"What does 'HTTPS' in a web address indicate?",
     "options":["The site is fast","The site is secure & encrypted","The site is free","The site is in English"],"a":1},
    {"q":"Which of these is a strong password?",
     "options":["123456","password","Rh7$kP9!mZ2q","yourname2024"],"a":2},
    {"q":"What is UPI used for?",
     "options":["Sending emails","Instant money transfers","Editing photos","Video calling"],"a":1},
    {"q":"An email asking for your bank OTP is most likely…",
     "options":["A reward","A phishing scam","A government notice","Spam folder error"],"a":1},
    {"q":"Which app stores official digital documents in India?",
     "options":["Google Drive","DigiLocker","WhatsApp","Notepad"],"a":1},
    {"q":"Two-factor authentication (2FA) adds…",
     "options":["A second verification step","More storage","Faster internet","Free apps"],"a":0},
    {"q":"Which is NOT a web browser?",
     "options":["Chrome","Firefox","Windows","Edge"],"a":2},
    {"q":"Before paying via UPI QR code you should…",
     "options":["Verify receiver name & amount","Share your PIN","Send a test of ₹500","Disable internet"],"a":0},
    {"q":"Cyberbullying should be…",
     "options":["Ignored forever","Reported & blocked","Replied to angrily","Shared publicly"],"a":1},
    {"q":"What does the UMANG app provide?",
     "options":["Games","Government services in one place","Movie tickets","Food delivery"],"a":1},
]

RESOURCES = [
    {"title":"DigiLocker","url":"https://www.digilocker.gov.in","desc":"Official digital document wallet by Government of India."},
    {"title":"UMANG","url":"https://web.umang.gov.in","desc":"Unified mobile app for all government services."},
    {"title":"Cyber Crime Portal","url":"https://cybercrime.gov.in","desc":"Report cybercrime & online fraud."},
    {"title":"Google Digital Unlocked","url":"https://learndigital.withgoogle.com","desc":"Free digital skills training by Google."},
    {"title":"NPCI – UPI","url":"https://www.npci.org.in/what-we-do/upi/product-overview","desc":"Learn how UPI works officially."},
    {"title":"Stay Safe Online","url":"https://staysafeonline.in","desc":"Cyber-safety tips for Indian citizens."},
]

# ---------- Routes ----------
@app.route("/")
def home():
    return render_template("home.html", stats={"modules":len(MODULES),"questions":len(QUIZ),"users":"1,200+"})

@app.route("/modules")
def modules():
    return render_template("modules.html", modules=MODULES)

@app.route("/resources")
def resources():
    return render_template("resources.html", resources=RESOURCES)

@app.route("/documentation")
def documentation():
    return render_template("documentation.html")

@app.route("/contact", methods=["GET","POST"])
def contact():
    if request.method == "POST":
        name=request.form.get("name","").strip()
        email=request.form.get("email","").strip()
        msg=request.form.get("message","").strip()
        if name and email and msg:
            con=db()
            con.execute("INSERT INTO contacts(name,email,message,created_at) VALUES(?,?,?,?)",
                        (name,email,msg,datetime.utcnow().isoformat()))
            con.commit(); con.close()
            return render_template("contact.html", success=True)
    return render_template("contact.html", success=False)

# ---------- Quiz ----------
@app.route("/quiz", methods=["GET","POST"])
def quiz_start():
    if request.method == "POST":
        session["quiz_name"] = request.form.get("name","Student").strip() or "Student"
        session["quiz_idx"] = 0
        session["quiz_answers"] = []
        return redirect(url_for("quiz_question"))
    return render_template("quiz_start.html", total=len(QUIZ))

@app.route("/quiz/q", methods=["GET","POST"])
def quiz_question():
    if "quiz_idx" not in session:
        return redirect(url_for("quiz_start"))
    idx = session["quiz_idx"]
    if request.method == "POST":
        ans = request.form.get("answer")
        answers = session.get("quiz_answers", [])
        answers.append(int(ans) if ans is not None and ans.isdigit() else -1)
        session["quiz_answers"] = answers
        idx += 1
        session["quiz_idx"] = idx
        if idx >= len(QUIZ):
            return redirect(url_for("quiz_result"))
    if idx >= len(QUIZ):
        return redirect(url_for("quiz_result"))
    q = QUIZ[idx]
    return render_template("quiz_question.html", q=q, idx=idx, total=len(QUIZ))

@app.route("/quiz/result")
def quiz_result():
    answers = session.get("quiz_answers", [])
    name = session.get("quiz_name","Student")
    score = sum(1 for i,a in enumerate(answers) if i < len(QUIZ) and a == QUIZ[i]["a"])
    total = len(QUIZ)
    passed = score >= 6
    con=db()
    con.execute("INSERT INTO quiz_results(name,score,total,passed,created_at) VALUES(?,?,?,?,?)",
                (name,score,total,1 if passed else 0,datetime.utcnow().isoformat()))
    con.commit(); con.close()
    return render_template("quiz_result.html", name=name, score=score, total=total, passed=passed)

@app.route("/certificate")
def certificate():
    name = session.get("quiz_name")
    answers = session.get("quiz_answers", [])
    if not name or not answers:
        return redirect(url_for("quiz_start"))
    score = sum(1 for i,a in enumerate(answers) if i < len(QUIZ) and a == QUIZ[i]["a"])
    if score < 6:
        return redirect(url_for("quiz_result"))
    return render_template("certificate.html", name=name, score=score, total=len(QUIZ),
                           date=datetime.utcnow().strftime("%B %d, %Y"))

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
else:
    init_db()
