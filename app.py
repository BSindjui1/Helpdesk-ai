from flask import Flask, render_template, request

app = Flask(__name__)

# Temporary in-memory storage — we'll replace this with a database later
tickets = []

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/submit", methods=["POST"])
def submit_ticket():
    name = request.form.get("name")
    issue = request.form.get("issue")

    ticket = {
        "name": name,
        "issue": issue
    }

    tickets.append(ticket)
    print(f"New ticket received: {ticket}")  # watch your terminal when you submit

    return f"<h2>Ticket received!</h2><p>Issue logged: {issue}</p><a href='/'>Submit another</a>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
