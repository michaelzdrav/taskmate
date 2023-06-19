# TaskMate
Heres a basic to do list to keep you accountable of your tasks. Simply register your own user, create a task with a title, due date and description. Each task can have comments made.

When your task is overdue, you will see an "Overdue" message displayed, along with an increment of the overdue task counter in the UI. Once completed, move the task to Done. Otherwise, Delete the task to be lost forever.

### Live Demo
http://taskmate.digital

## Features

- Multitenancy with a shared database schema
- Basic Authentication
- Secure session management protected by IP and login device
- Written in Flask with gunicorn for performance
- Feature rich To Do list
- Easy ability to self host via cli or Docker
- Application wide logging
- SMTP support
- Clean and simple UI
- Postgres, SQLite support
- Timezone support

## Setup
Initialise the database and virtual environment. 
🚨 Please note that psycopg2 is needed for ```make db``` but needs to be removed when building the Docker image.

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

- [x] CI/CD pipeline to build image and push to Dockerhub
- [x] Add pytest coverage
- [x] Introduction of testing using pytests
- [x] Proper logging instead of just printing values everywhere
- [x] Redesigned frontend using Bootstrap
- [x] Add edit & delete for comments
- [x] Deploying this in AWS
- [x] Add get_task before anything that uses the existing task to check it exists
- [x] Switch to flask-sqlalchemy to support more db engines
- [x] Add timezone support
- [ ] Test errors - redirect with flash instead of continuing with flash  ⌛
- [ ] SMTP integration for notifications (task creation/overdue/comments left)
- [ ] Add advanced pytests ⌛
- [ ] Refactoring ⌛
  - [ ] Removed unused packages:
    - https://stackoverflow.com/questions/25376213/delete-unused-packages-from-requirements-file
  - [ ] Clean up HTML
  - [ ] Refactor application structure
- [ ] Input validation, text length limits for title, description, comments
- [ ] File uploads for each task
- [ ] Add caching for performance
- [ ] Introduce background tasks with celery (for emails etc) to reduce waiting times   ⌛
  - https://flask.palletsprojects.com/en/2.3.x/patterns/celery/
- [ ] Improve security
  - [ ] Enable HTTPS
  - [ ] Flask-talisman
  - [x] Flask-paranoid
  - [ ] Password Reset
  - [ ] Password complexity
  - [ ] Account verification
- [ ] Fix text wrapping on mobile/desktop view
- [ ] Pytest for Flask-SQLAlchemy: https://github.com/jeancochrane/pytest-flask-sqlalchemy
- Need to fix the images as they don't work from github anymore