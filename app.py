from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import anthropic
import os

app = Flask(__name__)


# This Tells Flask Where to create the database file
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tickets.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# This is my database table defined as a python class
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


def triage_ticket(issue_text):
    try:
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
#Create the database file and tables on first run
with app.app_context():
    db.create_all()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/submit", methods=["POST"])
def submit_ticket():
    name = request.form.get("name")
    issue = request.form.get("issue")
    category = request.form.get("category")

    # Get AI triage
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

@app.route("/tickets")
def view_tickets():
    all_tickets = Ticket.query.order_by(Ticket.submitted_at.desc()).all()
    return render_template("tickets.html", tickets=all_tickets)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
