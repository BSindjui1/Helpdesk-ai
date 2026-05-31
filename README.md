# AI Help Desk Ticketing Assistant

A web-based ticketing system built with Python and Flask, running on a Raspberry Pi.
Users can submit IT support tickets which are categorized and (soon) triaged by AI.

## How to Run
1. Activate virtual environment: source venv/bin/activate
2. Run: python3 app.py
3. Open browser to http://YOUR_PI_IP:5000

What I’ve Done So Far

Set Up Environment:

Initialized a virtual environment on my Raspberry Pi.

Ran system updates (sudo apt update && sudo apt upgrade -y).

Confirmed Python and pip versions.

Project Structure Initialization:

Created the helpdesk-ai directory with templates and static folders.

Added initial files: app.py, requirements.txt, README.md, and devlog.md.

Virtual Environment & Package Management:

Set up the virtual environment (python3 -m venv venv) and activated it.

Installed required packages and saved them to requirements.txt.

Initial App Setup:

Created the basic Flask app (app.py) and set it to run in debug mode on 0.0.0.0.

Added a form for submitting tickets and a tickets.html page to display all tickets.

Recent Update (Phase 2):

Implemented the tickets list page to display submitted tickets.

Confirmed that the table dynamically updates and sorts tickets by submission time.

 I designed and implemented a database schema for a ticketing system
 I used SQLAlchemy ORM to interact with a SQLite database
 I built a data display page that queries and renders live database records
 I understand the difference between in-memory storage and persistent disk storage
