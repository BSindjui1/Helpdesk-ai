In the last 24 hours, I made a helpdesk-ai folder. Within that folder i made two folders named templates and static.
I then used "touch app.py requirements.txt README.md", it seems to be a simplier way of creating these files. When
creating those files indiviually in the cmd line i run into errors repeatedly. so now i have app.py the core of my app a templates folder which my flask wi>
## 2025-05-26
-Basically restarted the whole process
-updated my pi using "sudo apt update && sudo apt upgrade -y"
-Checked for python, pip3, and added venv support "sudo apt install python3-venv -y"
Currently the model looks like this

helpdesk-ai/
-app.py
-templates/
-README.md
-devlogs.md
-Static/
-requirements.txt

I then setup my virtual environmet and then install flask and use "pip freeze>pip freeze > requirements.txt",
which creates a list of all the python packages installed in my environment. I tried running pip install flask
without activating venv("source venv/bin/activate"), and that resulted in there being an error due to the
environment being managed externally, which means I didn't have the right packages avaliable, when i run it in the venv
it puts all the dependecies and settings.

1.What is a package manager and why does Linux use one?
-A package manager on linux helps you install, update, and manage software pacLinux uses a package manager to keep 
everything organized and to ensure that software is easy to install and update. 
2.Why do we separate templates/ and static/ folders?
-Templates is where the main content is. Flask uses Templates to render the HTMl pages. Static folder is for things 
like CSS,JavaScript, images, fonts, etc. Keeping these folders seperate helps flask processes them efficiently.
3.What would happen if two projects on the same machine used different versions of Flask without virtual environments?
-If two projects on the same machine try to use a different versions of flask with venv, it would cause complications in errors. 
The systems venv can only hold 1 version of a package at a time. So trying to run both without a venv could result in one breaking.
4.What does pip freeze actually do? Where does it get that information from?
-Pip freeze generates a list of all the installed packages and their versions.

I now wrote the code for nano app.py and index.html within the templates folder, and then ran the app. I was able too pull
up the app when i typed my pi's public ip, but i believe the static ip isn't working. and when i type in a ticket im able to see it.
within the cmd line. While trying to break it and see how some of the individual layers run. I got this error that would say "Method Not Allowed" When
I Would submit a ticket. I thought it pointed to the route in the app.py file, but it was because of a single character within the index.html file
<form action="/submit" method-"POST"> this was the wrong one <form action="/submit" method="POST"> thats the correct one it was that single -Dash
When I change the request.form.get("name") to ("username") In the terminal it now displays "none" for its name. When i change the name of the templates
folder I get a message that says jinja2.exceptions.TemplateNotFound
