from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import anthropic
import os

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tickets.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

# --- MODELS ---

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    issue = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default="Open")
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    ai_category = db.Column(db.String(50), default="Pending")
    ai_priority = db.Column(db.String(20), default="Pending")
    ai_suggestion = db.Column(db.Text, default="Pending")

    def __repr__(self):
        return f"<Ticket {self.id} - {self.name}>"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- AI TRIAGE ---

def triage_ticket(issue_text):
    try:
        print(f"Sending to AI: {issue_text[:50]}...")
        client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        messages = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=300,
            messages=[
                {
                    "role": "user",
                    "content": f"""You are an IT help desk triage assistant.

Analyze this support ticket and respond in exactly this format with no extra text:
CATEGORY: [Hardware/Software/Network/Account/Other]
PRIORITY: [Low/Medium/High]
SUGGESTED FIX: [One sentence max]

Ticket: {issue_text}"""
                }
            ]
        )
        response_text = messages.content[0].text
        lines = response_text.strip().split('\n')
        ai_category = lines[0].replace("CATEGORY:", "").strip()
        ai_priority = lines[1].replace("PRIORITY:", "").strip()
        ai_suggestion = lines[2].replace("SUGGESTED FIX:", "").strip()
        return ai_category, ai_priority, ai_suggestion
    except Exception as e:
        print(f"AI triage failed: {e}")
        return "Unknown", "Unknown", "AI triage unavailable"

# --- ROUTES ---

with app.app_context():
    db.create_all()
    # Create default admin user if none exists
    if not User.query.filter_by(username="admin").first():
        admin = User(username="admin")
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()
        print("Default admin user created: admin / admin123")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/submit", methods=["POST"])
def submit_ticket():
    name = request.form.get("name")
    issue = request.form.get("issue")
    category = request.form.get("category")
    ai_category, ai_priority, ai_suggestion = triage_ticket(issue)
    new_ticket = Ticket(
        name=name,
        issue=issue,
        category=category,
        ai_category=ai_category,
        ai_priority=ai_priority,
        ai_suggestion=ai_suggestion
    )
    db.session.add(new_ticket)
    db.session.commit()
    print(f"Ticket saved: {new_ticket} | AI Priority: {ai_priority}")
    return f"""
        <h2>Ticket Received!</h2>
        <p><strong>Issue:</strong> {issue}</p>
        <p><strong>Ticket ID:</strong> {new_ticket.id}</p>
        <hr>
        <h3>AI Triage Result:</h3>
        <p><strong>Category:</strong> {ai_category}</p>
        <p><strong>Priority:</strong> {ai_priority}</p>
        <p><strong>Suggested Fix:</strong> {ai_suggestion}</p>
        <br>
        <a href='/'>Submit another</a> | <a href='/tickets'>View all tickets</a>
    """

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("view_tickets"))
        return render_template("login.html", error="Invalid username or password")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/tickets")
@login_required
def view_tickets():
    all_tickets = Ticket.query.order_by(Ticket.submitted_at.desc()).all()
    return render_template("tickets.html", tickets=all_tickets)

@app.route("/update_status/<int:ticket_id>", methods=["POST"])
@login_required
def update_status(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    new_status = request.form.get("status")
    ticket.status = new_status
    db.session.commit()
    print(f"Ticket {ticket_id} status updated to: {new_status}")
    return redirect(url_for("view_tickets"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
