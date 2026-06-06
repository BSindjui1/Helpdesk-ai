# Dev Log — AI Help Desk Ticketing Assistant

---

## Phase 1 — Foundation

### Initial Setup (Day 1)

I started by creating the `helpdesk-ai` project folder and setting up the basic structure. Inside it, I created two subfolders, `templates` and `static`, and used the `touch` command to create `app.py`, `requirements.txt`, and `README.md` all at once. I found that using `touch` was much cleaner than creating files individually through the command line, where I kept running into errors.

The project structure looked like this:

```
helpdesk-ai/
├── app.py
├── templates/
├── static/
├── README.md
├── devlogs.md
└── requirements.txt
```

**What I learned:** `app.py` is the core of the Flask application. The `templates/` folder is where Flask looks for HTML files to render. The `static/` folder holds CSS, JavaScript, images, and fonts. Keeping them separate lets Flask process them efficiently and mirrors how real production web servers are structured.

---

### 2025-05-26 — Full Restart & Environment Setup

I decided to restart the whole process cleanly. The first thing I did was update the Pi:

```bash
sudo apt update && sudo apt upgrade -y
```

Then I confirmed Python and pip were installed, and added virtual environment support:

```bash
sudo apt install python3-venv -y
```

I set up the virtual environment and installed Flask:

```bash
python3 -m venv venv
source venv/bin/activate
pip install flask
pip freeze > requirements.txt
```

One important experiment: I tried running `pip install flask` *without* activating the virtual environment first. It threw an error about the environment being "externally managed." This showed me that the system Python environment on Raspberry Pi OS is protected; you have to work inside a virtual environment to install packages for your own projects.

**Key concept — Virtual Environments:** A virtual environment is an isolated Python installation that exists only within your project folder. Every time you open a new terminal, you have to activate it again with `source venv/bin/activate`. If you forget, Python defaults to the global environment, and none of your project packages are available. The `(venv)` prefix in your terminal prompt tells you it's active.

**Why `pip freeze > requirements.txt` matters:** This saves a list of every installed package and its exact version. Any machine, server, or Docker container can then run `pip install -r requirements.txt` to recreate your exact environment. This is one of the most important habits in DevOps.

**Concept Check Answers:**

*What is a package manager, and why does Linux use one?*
A package manager helps you install, update, and manage software. Linux uses one to keep everything organized and ensure software is easy to install, update, and remove consistently across the system.

*Why separate `templates/` and `static/` folders?*
`templates/` is where Flask looks for HTML files to render dynamic pages. `static/` holds files that never change, like CSS, JavaScript, and images. Separating them lets Flask and web servers like Nginx handle each type efficiently.

*What happens if two projects share Flask versions without virtual environments?*
The system can only hold one version of a package at a time globally. Two projects needing different versions would break each other. Virtual environments solve this by giving each project its own isolated space.

*What does `pip freeze` actually do?*
It reads all packages currently installed in the active environment and outputs them with their exact version numbers. The `> requirements.txt` part saves that output to a file.

---

### 2025-05-26 — First Working Ticket Form

I wrote `app.py` and `templates/index.html` and ran the app for the first time. I was able to reach it by typing my Pi's IP address in my browser, and when I submitted a ticket, it printed in the terminal. Seeing that work for the first time was a big moment.

**Intentional breaking experiments:**

- Removed `methods=["POST"]` from the `/submit` route → got "Method Not Allowed." The browser sends a POST request when you submit a form, but without specifying that, Flask only accepts GET by default.
- Changed `request.form.get("name")` to `request.form.get("username")` → the terminal printed `None` for the name field. The form field's `name` attribute has to match exactly what you ask for in Python.
- Renamed `templates/` to `template/` → got `jinja2.exceptions.TemplateNotFound`. Flask is hardcoded to look in a folder called `templates` — the name is not optional.

**Concept Check Answers:**

*POST vs GET?*
POST sends data to the server used when submitting a form or creating something. GET retrieves data used when loading a page. The key difference is that POST has a request body; GET puts everything in the URL.

*Why does `host="0.0.0.0"` let other devices connect?*
It tells Flask to listen on all network interfaces, not just the local one. `127.0.0.1` (localhost) only allows the Pi itself to connect. `0.0.0.0` lets any device on the same network reach it.

*Why never use `debug=True` in production?*
Debug mode shows detailed error pages with your code and file paths visible to anyone, which is a major security risk. It also auto-reloads on code changes, which is useful for development but unpredictable on a live server.

*What does the `name` attribute on an HTML input do?*
It labels the field, so Flask knows what to call it when the form is submitted. Without it, that field's data is not included in the form submission at all.

*Why do tickets disappear on restart?*
They're stored in a Python list in RAM. RAM is wiped when the app stops. A database stores data on disk, which persists across restarts.

---

## Phase 2 — Database

### 2025-05-28 — SQLite Database with SQLAlchemy

Today I wired up a real database so tickets would survive restarts. I installed Flask-SQLAlchemy and rewrote `app.py` to define a `Ticket` model as a Python class. SQLAlchemy acts as an ORM (Object Relational Mapper); it translates my Python code into SQL automatically, so I don't have to write raw SQL queries.

The core concept I understood today: **RAM is temporary, disk is permanent.** A Python list lives in RAM and disappears when the app stops. A SQLite database is a single file on disk — `instance/tickets.db` — that stays there until you delete it.

**Intentional breaking experiments:**

- Changed `nullable=False` to `nullable=True` on the name field. Logically, this would allow empty names, but I didn't see a difference because the HTML form's `required` attribute blocks the submission at the browser level before it even reaches Flask. Two layers of validation: one in the browser, one in the database.
- Submitted 3 tickets, restarted the app, submitted 1 more → got Ticket ID 4. The ID counter persists because it's stored in the database file on disk, not in Python memory.
- Deleted `instance/tickets.db` with `rm instance/tickets.db`, restarted → all tickets gone. The entire database lives in that one file. This is exactly why backups exist.

**Concept Check Answers:**

*What is an ORM?*
Software that lets you use Python objects instead of writing raw SQL. SQLAlchemy translates my Python code into SQL commands automatically.

*What does `db.session.commit()` do?*
It permanently saves staged changes to the database file. `db.session.add()` only stages a record in memory, like `git add`. `db.session.commit()` writes it to disk, like `git commit`. Without the commit, nothing is actually saved.

*What is a primary key?*
A unique identifier for each row. No two rows can share one. It lets the database find, update, or delete the exact right record every time.

*What does `nullable=False` mean?*
It forces that field to always have a value. If something tries to save a record with that field empty, the database rejects it.

*Why does Flask put the database in `instance/`?*
That folder is designed for data that changes and should not be part of the codebase. It is not tracked by Git by default, which keeps the database file out of version control, which is important for both security and clean commits.

---

### 2025-05-29 — Ticket Viewer Page

I added a `/tickets` route to `app.py` and created `tickets.html` in the templates folder. This page queries the database and displays all tickets in a table, sorted newest first using `.order_by(Ticket.submitted_at.desc())`.

I learned that `{% if %}` and `{% for %}` are Jinja2 syntax; flask's templating language. It lets you write Python logic directly inside HTML. The `{{ ticket.name }}` syntax inserts a value from Python into the page. Every major web framework has a version of this.

**Experiment:** Changed `{{ ticket.name }}` to `{{ ticket.username }}`. Flask displayed a blank value, not an error, because `username` doesn't exist on the Ticket model. Jinja2 renders missing attributes as empty rather than crashing.

**Concept Check Answers:**

*What is Jinja2?*
A templating engine that connects Python and HTML. HTML alone is static; it can't change based on data. Jinja2 lets Python values, conditions, and loops be written directly into HTML so pages update dynamically based on what's in the database.

*What does descending mean in a query?*
Newest to oldest, or largest to smallest. The opposite is ascending from oldest to newest. Descending puts the most recent ticket at the top of the list.

*Is `.all()` a good idea with 10,000 tickets?*
No. Loading everything at once would be slow and overwhelming. The solution is pagination, loading 20 or 50 tickets at a time with next/previous controls.

*Is the `/tickets` page a security problem if it's public?*
Yes. Tickets can contain sensitive information. The fix is authentication, a login system, so only authorized staff can view the dashboard.

*Python Ticket class vs. database table — are they the same?*
Related but not the same. The class is the blueprint that defines what fields a ticket has. The table is the actual storage where real data lives. The class tells SQLAlchemy how to create and interact with the table.

---

### 2025-05-29 — Bug Fix: /tickets Showing "Not Found"

**What happened:** After creating `tickets.html`, going to `/tickets` returned a 404 Not Found error.

**How I diagnosed it:** Ran `cat app2.py` to inspect the code and check if the route existed.

**Bugs found (3 total):**

1. Missing `@` on the route decorator — `app.route('/tickets')` instead of `@app.route("/tickets")`. Without the `@`, Python never registers it as a route. It's just a function that never gets called.
2. Wrong separator in the query — `Ticket.submitted_at_desc()` instead of `Ticket.submitted_at.desc()`. The underscore made Python look for a method that doesn't exist. The dot is required because `.desc()` is called *on* the column.
3. Typo in `render_template` — wrote `render_templates` with an extra `s`. Flask has no function by that name.

**What I learned:** A 404 doesn't always mean the URL is wrong. It can mean the route was never registered in the first place. `grep "tickets" app.py` is a fast way to check without reading the whole file. Three bugs in six lines slow down and read code character by character.

---

### 2025-05-29 — Bug Fix: Packages Installed Globally

**What happened:** Installed `flask_sqlalchemy` outside the virtual environment. When I activated the venv later, the package wasn't available.

**Fix:**
```bash
pip uninstall flask_sqlalchemy
source venv/bin/activate
pip install flask_sqlalchemy
```

**Lesson learned:** The virtual environment is completely isolated. Installing a package globally doesn't make it available inside the venv, and vice versa. Always confirm `(venv)` is showing in your prompt before running any `pip install` command.

---

## Phase 3 — AI Integration

### 2025-05-31 — Connecting the Claude API

**The goal:** Right now, when a ticket is submitted, nothing intelligent happens. A real Tier 1 help desk agent reads it and figures out the category, urgency, and likely fix. I wanted to automate that first pass using the Claude API — so every ticket gets triaged automatically with a category, priority level, and suggested fix.

**Steps taken:**
1. Created an API key at console.anthropic.com
2. Stored it as an environment variable in `~/.bashrc` — never hardcoded in the source files
3. Installed the `anthropic` Python library inside the venv
4. Wrote a standalone `test_ai.py` script to test the API call in isolation before touching `app.py`

**Why environment variables for secrets:** Anthropic actively scans GitHub for exposed API keys and revokes them immediately. If a key is hardcoded in a file and pushed to a public repository, it's compromised. Environment variables keep secrets out of the code entirely. This is standard practice at every company, like AWS, Azure, and every real DevOps pipeline uses this same pattern.

**Key experiment:** Ran `echo $ANTHROPIC_API_KEY` in a new terminal without sourcing `.bashrc`. It showed nothing. Environment variables only exist in the session where they were exported. Each new terminal starts fresh.

**Concept Check Answers:**

*What is an API?*
A set of rules that lets one program talk to another service. Making an API call means sending a request to that service and asking it to do something or return data.

*What is an API key?*
Credentials that identify your application to an external service. Different from a password because it's meant for software, not people.

*What does `export` do in bash?*
Makes the variable available to any programs or scripts launched from that terminal session.

*How would a teammate get the API key?*
They would set up the same environment variable on their own machine in their own `.bashrc`. The key is never shared through the code itself.

---

### 2026-06-01 — Wiring AI Into the App

I wrote the test script first, confirmed the API worked, and then integrated it into `app.py`. The `triage_ticket()` function sends the issue text to Claude and parses the structured response into category, priority, and suggested fix. Each of these gets saved to the database alongside the ticket.

**Bugs encountered:**
- Several typos from typing too fast: a `.` before `os`, a missing closing parenthesis, a dash instead of `=` on the model name, and a variable named `messages` that I tried to read as `message`
- A `TabError` from mixing tabs and spaces in indentation. Python uses indentation to define code blocks — tabs and spaces look the same to your eyes, but Python treats them as completely different characters. Rule going forward: always use 4 spaces, never Tab
- After rewriting `app.py` to fix the TabError, I accidentally deleted the `/tickets` route. The link existed in the HTML, but Flask had no route to handle it. Diagnosed with `cat app.py | grep "tickets"` which showed only two matching lines instead of the expected route definition

**Phase 3 milestone:** Submitted a ticket — "My phone won't connect to the internet, but my laptop connects fine" — and got back:
- Category: Network
- Priority: High
- Suggested Fix: Restart your phone's WiFi, check if airplane mode is enabled, and verify you're connected to the correct network

The full pipeline was working end to end.

**Concept Check Answers:**

*What is a try/except block?*
"Try to run this code, and if something goes wrong, run this other code instead." The API call is wrapped in one so that if it fails due to a bad key, rate limit, or network issue, the app catches the error gracefully and returns fallback values instead of crashing.

*What if the AI doesn't follow the exact format?*
The parsing would break. To make it more robust, you'd write code that handles small deviations, looser matching, default values, or a retry with a cleaner prompt.

*Why delete the database when adding new columns?*
SQLite doesn't automatically update existing tables when you add new columns to your model. In development, deleting and recreating is the simplest fix. In production, you'd use database migrations to update the schema without losing data.

*What is a database migration?*
Moving data from one structure to another without losing it. Production systems can't just delete the database where real user data lives. Migrations update the schema safely while preserving existing records.

*What could go wrong with one API call per ticket at scale?*
Rate limits, slow response times, increased cost, and error stacking if too many requests come in at once. Solutions include caching, batching requests, or using a queue system.

---

## Phase 4 — Admin Dashboard & Authentication

### 2026-06-02 — CRUD Operations and Status Management

CRUD stands for Create, Read, Update, and Delete, which are the four fundamental operations of any database-driven application. By this point, I had Create (submit ticket) and Read (view tickets) working. Today I added an update.

I added an `/update_status/<ticket_id>` route to `app.py` and rewrote `tickets.html` to include a status dropdown and update button for each ticket. Statuses can now be changed between Open, In Progress, and Resolved, and the changes persist across restarts because they're saved to the database.

**Experiments:**
- Changed a ticket to Resolved, restarted the app, and the status was still Resolved. Confirmed that status is stored in the database, not in memory.
- Removed `methods=["POST"]` from the update route → got a 405 Method Not Allowed error. Without specifying POST, Flask defaults to GET only. Status updates have to be POST because they change data on the server.
- Typed `/update_status/999` manually → got a 404. `get_or_404()` automatically returns a 404 response when the requested record doesn't exist, so you don't have to handle that case manually.

**Concept Check Answers:**

*`redirect()` vs `render_template()`?*
Use `redirect()` after an action that changes data, which sends the user to a different URL. Use `render_template()` to display a page. After updating a ticket status, you redirect so the user sees the refreshed list, not a stale page.

*What is `get_or_404()`?*
A shortcut that queries the database for a record by ID and automatically returns a 404 response if it doesn't exist. Without it, you'd have to write that check manually every time.

---

### 2026-06-02 — Login System and Route Protection

I added Flask-Login to protect the admin dashboard. Only authenticated users can view or manage tickets. The implementation required installing `flask-login`, adding a `User` model to the database, writing login and logout routes, creating `login.html`, and adding `@login_required` decorators to every protected route.

Passwords are stored as hashes using Werkzeug, never as plain text. When you log in, your password is hashed and compared to the stored hash. The actual password is never saved anywhere.

**How `@login_required` works under the hood:** When an unauthenticated user hits a protected route, Flask-Login intercepts the request, stores where they were trying to go, redirects them to the login page, and after a successful login, sends them back to their original destination. The `login_manager.login_view = "login"` line in the app config controls where they get redirected.

**Experiments:**
- Accessed `/tickets` without logging in → redirected to login page automatically
- Logged out via `/logout`, tried `/tickets` again → redirected again. Confirmed logout works correctly
- Entered wrong password → "Invalid username or password" error displayed
- Removed `@login_required` from the `/tickets` route → page became accessible without logging in. Added it back immediately

**Concept Check Answers:**

*What is password hashing?*
A transformation that turns a password into a unique string of characters. You can't reverse it to get the original password back. When someone logs in, their input is hashed, compared to the stored hash, the real password is never saved.

*What does a session cookie do?*
It stores your login state in the browser so the server knows you're still authenticated between page loads. Without it, you'd have to log in on every single request.

*Authentication vs. authorization?*
Authentication confirms who you are. Authorization determines what you're allowed to do. Logging in is authentication. Being allowed to access the admin dashboard is authorization.

*Why is `admin123` a problem in production?*
It's the first password anyone would try. Default credentials are one of the most common entry points for attacks. In production, passwords should be strong, unique, and set by the user, not hardcoded in the source code.

---

## Phase 5 — DevOps Layer

### 2026-06-03 — systemd Service

The problem with the app until now: it only ran when I was logged into the Pi and had manually typed `python3 app.py`. The moment I closed the terminal, the app died. A real server runs 24/7 without anyone babysitting it.

I created a systemd service file at `/etc/systemd/system/helpdesk.service`. systemd is the Linux service manager — it controls every background process on the Pi, from WiFi to SSH. By registering my app as a service, it starts automatically on boot and restarts itself if it crashes.

**Bug encountered:** The service kept failing with `status=217/USER`. Running `sudo journalctl -u helpdesk -n 20` revealed the exact error: "Failed to determine user credentials." The service file had the wrong username; I had used the Pi's hostname instead of the actual Linux username. These are two different things. Fixed by correcting every path in the service file and reloading with `sudo systemctl daemon-reload`.

**Second issue:** Accidentally exposed my API key. Immediately revoked it at console.anthropic.com and generated a new one. Updated the key in both the service file and `~/.bashrc`. Important lesson: treat API keys like passwords, revoke immediately if exposed anywhere.

**After the fix:** Rebooted the Pi with `sudo reboot`. After 30 seconds, I opened the browser, and the app was running without me doing anything. That's what a real server looks like.

**Concept Check Answers:**

*What is a daemon?*
A background process that runs without direct user interaction. The word comes from Unix terminology. systemd manages all daemons on a Linux system.

*What does `After=network.target` mean?*
It tells systemd not to start the app until the network is up. Since the app listens on a network port and calls an external API, starting before the network is ready would cause it to fail immediately.

*`systemctl enable` vs `systemctl start`?*
`enable` registers the service to start automatically at boot. `start` launches it immediately right now. You typically do both when setting up a new service.

*What does `Restart=always` do?*
If the app crashes for any reason, systemd automatically restarts it after the `RestartSec` delay. Without `RestartSec`, a persistent bug could cause a very fast restart loop that hammers the system.

*How to check memory and CPU usage?*
Run `htop` on the Pi for a live view of all running processes and their resource usage.

---

### 2026-06-03 — Docker

Docker is the single most important DevOps tool I've worked with in this project. A Dockerfile is a recipe that packages the entire app, including Python, Flask, and all dependencies, into a container that runs identically on any machine.

I installed Docker on the Pi, created a `.dockerignore` file to exclude `venv/`, `instance/`, and other unnecessary files, then wrote the Dockerfile. The key insight about Docker's layer caching: copy `requirements.txt` and install dependencies *before* copying the rest of the code. That way, Docker only re-runs the install step when dependencies actually change, not on every code change.

**Port conflict:** When I tried to run the Docker container, I got an "address already in use" error on port 5000. The systemd service was already running on that port. Two processes can't share the same port. Stopped the systemd service first, then ran the Docker container successfully.

**Key Docker concepts:**
- A Docker image is the blueprint, a snapshot of your app and all its dependencies
- A Docker container is a running instance of that image
- Containers are lightweight because they share the host OS kernel, unlike virtual machines, which each run their own full OS
- Docker volumes solve the data persistence problem; without them, the database is lost when the container stops

**Useful commands learned:**
```bash
docker ps          # show running containers
docker ps -a       # show all containers, including stopped
docker images      # show built images
docker stop ID     # stop a container
docker logs ID     # view container output
```

---

### 2026-06-03 — Deployment Script

A deployment script takes the process of "I made a code change" and turns it into a single command that updates and restarts everything automatically. This is the manual version of what CI/CD pipelines do. Understanding it manually means I'll understand the automated version when I encounter it at a job.

The script stops the service, updates dependencies, restarts the service, waits 3 seconds, then checks whether it came back up successfully. If it didn't, it tells you exactly what command to run to see the logs.

`chmod +x deploy.sh` makes the file executable; Linux doesn't run scripts by default. The `#!/bin/bash` line at the top tells the system which interpreter to use.

**Concept Check Answers:**

*What is CI/CD?*
Continuous Integration / Continuous Deployment is an automated pipeline that tests and deploys code every time a change is pushed to the repository. My deploy script is the manual version of what tools like GitHub Actions do automatically.

*What does `sleep 3` do in the script?*
Waits 3 seconds after restarting the service before checking its status. Without the wait, the check would run before systemd has had time to fully start the app, and it might incorrectly report failure.

