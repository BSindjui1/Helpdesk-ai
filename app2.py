from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

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

   def __repr__(self):
       return f"<Ticket {self.id} - {self.name}>"

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

    new_ticket = Ticket(name=name, issue=issue, category=category)
    db.session.add(new_ticket)
    db.session.commit()

   


    print(f"Ticket saved to database: {new_ticket}")
    return f"<h2>Ticket received!</h2><p>Issue logged: {issue}</p><p> Ticket ID: {new_ticket.id}</p><a href='/'Submit another</a>"

@app.route("/tickets")
def view_tickets():
    all_tickets = Ticket.query.order_by(Ticket.submitted_at.asc()).all()
    return render_template("tickets.html", tickets=all_tickets)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
