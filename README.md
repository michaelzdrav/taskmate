# TaskMate
Heres a basic to do list to keep you accountable of your tasks. Simply register your own user, create a task with a title, due date and description. Each task can have comments made.

When your task is overdue, you will see an "Overdue" message displayed, along with an increment of the overdue task counter in the UI. Once completed, move the task to Done. Otherwise, Delete the task to be lost forever.

Please make sure to remove the <b>test</b> user in <b>web/db.py</b> if you are going to expose this to the Internet.

### Live Demo
http://taskmate.duckdns.org/


## Features

- Basic Authentication
- Written in Flask
- Feature rich To Do list
- Easy ability to self host via cli or Docker
- Application wide logging
- SMTP support
- Clean and simple UI
- SQLite database support (more options coming)

## Dependencies
- Make sure you have sqlite3 installed locally

## Setup
Initialise the database and virtual environment.
```bash
  virtualenv venv
  source venv/bin/active
  venv/bin/pip install -r requirements.txt
  make env db 
```

Please change any values needed in ```.env```


## Run locally
Run with the ```Makefile```
```bash
  make run
```
You can run with debug mode enabled with the ```Makefile```
```bash
  make debug
```
## Building the Docker image
Run with the ```Makefile```
```bash
  make build
```
## Docker

#### Run with docker-compose (development environment)

```bash
  make docker-dev
```
Please change any values needed in ```.env``` and ```docker-compose/docker-compose-dev.yaml```


#### Run with docker-compose (production environment)

```bash
  make docker
```
Please change any values needed in ```.env``` and ```docker-compose/docker-compose.yaml```


## Testing

Run Pytest against the code, including test coverage

```bash
  make test sast
```

Inspecting the database can be done using the Makefile also

```bash
  make db-view
```

## Authors

- [@michaelzdrav](https://www.github.com/michaelzdrav)

## Screenshots
### Creating a task:

![](/screenshots/create-task.png)

### Active tasks:

![](/screenshots/active-tasks.png)

### Done tasks:

![](/screenshots/done-tasks.png)

### First view upon login:

![](/screenshots/first-login.png)

### Email received after creating a task:

![](/screenshots/legacy/new-task-email.png)

## Roadmap 
Order depends on what I feel like working on when I have the free time 😃

- ~~CI/CD pipeline to build image and push to Dockerhub~~ 
- ~~Add pytest coverage (#TODO check out https://github.com/pytest-dev/pytest-cov)~~
- ~~Introduction of testing using pytests, (#TODO check out https://flask.palletsprojects.com/en/2.2.x/tutorial/tests/)~~
- ~~SMTP integration for notifications (task creation/overdue/comments left)~~
~~- Proper logging instead of just printing values everywhere~~
- ~~Redesigned frontend using Bootstrap~~
~~- Add edit & delete for comments~~
~~ - Updated UI ~~
~~- Deploying this in AWS~~
- Add advanced pytests ⌛
- Refactoring ⌛
  - Refactor create/update to use functions to check due_date 
- Input validation, text length limits for title, description, comments
- Add settings page, configure timezones, store tasks in local timezones 
- Add get_task before anything that uses the existing task to check it exists
- File uploads for each task
- Add caching for performance
- Switch to flask-sqlalchemy to support more db engines https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iv-database 
- Introduce background tasks with celery (for emails etc) to reduce waiting times 
  - https://flask.palletsprojects.com/en/2.3.x/patterns/celery/
- Improve security
  - Flask-talisman
  - Flask-paranoid
  - Password Reset
  - Password complexity
  - Account verification




# Contribution

These are some of the suggested contributions to **TaskMate**:

- Refactor code to use the concept of separation of concerns (each functionality resides as a stand-alond module)
  - Config module
  - DB Schema
  - Email
  - Application instance
  - Forms (using bootstrap to quicky generate and style them)
  - Migrations (all changes to db schema available for review)
- Modify the design of the database to support any engine
  - The default is SQLite (it is small, quick to setup, does not require a server)
  - If another is needed, then you can pass that as an environment variable in `.env`
- Application instance:
  - Refactored the factory function `create_app()` to not only initialize the extention variables but also to log errors (1. On file and 2. Send log data to admin via email)
- To ensure the emailing feature works all the time, locally and on a prod app, I have used Twilio Sendgrid (You will have to create your own accounts with Twilio and Sengrid. It is free.)
- All static resources are put in individual files as seen in the static folder
- Base template modified to truly make it a base that child templates find reusable elements only.


## UI Updates are as seen below:

### Landing page
![Landing page](/app/static/img/landing_page.png)

### Login Page
![Login page](/app/static/img/login_page.png)

- With links to register page, request password reset page and reset password page

### Home Page
![Home page](/app/static/img/home_page.png)

### Create Task Page (Standalone)
![Home page](/app/static/img/create_task_page.png)

### Create Task (Home page)
![Home create task page](/app/static/img/home_create_task_page.png)

### View Task
![View task page](/app/static/img/view_task_page.png)

### Edit Task
![Edit task page](/app/static/img/edit_task.png)

### Comment on Task
![Comment on task page](/app/static/img/comment_on_task.png)
