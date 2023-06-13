# TaskMate
Heres a basic to do list to keep you accountable of your tasks. Simply register your own user, create a task with a title, due date and description. Each task can have comments made.

When your task is overdue, you will see an "Overdue" message displayed, along with an increment of the overdue task counter in the UI. Once completed, move the task to Done. Otherwise, Delete the task to be lost forever.

Please make sure to remove the <b>test</b> user in <b>web/db.py</b> if you are going to expose this to the Internet.

### Live Demo
http://taskmate.duckdns.org/


## Features

- Multitenancy
- Basic Authentication
- Written in Flask
- Feature rich To Do list
- Easy ability to self host via cli or Docker
- Application wide logging
- SMTP support
- Clean and simple UI
- Postgres, SQLite support

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
~~- Updated UI~~
~~- Deploying this in AWS~~
~~- Add get_task before anything that uses the existing task to check it exists~~
~~- Switch to flask-sqlalchemy to support more db engines https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iv-database~~
- Add advanced pytests ⌛
- Refactoring ⌛
  - Refactor create/update to use functions to check due_date 
- Input validation, text length limits for title, description, comments
- Add settings page, configure timezones, store tasks in local timezones 
- File uploads for each task
- Add caching for performance
- Introduce background tasks with celery (for emails etc) to reduce waiting times 
  - https://flask.palletsprojects.com/en/2.3.x/patterns/celery/
- Improve security
  - Flask-talisman
  - Flask-paranoid
  - Password Reset
  - Password complexity
  - Account verification
- Fix text wrapping on mobile/desktop view
- Pytest for Flask-SQLAlchemy: https://github.com/jeancochrane/pytest-flask-sqlalchemy
- Regular Pytest
- Scheduled pg_cron for setting overdue date, and start sql-vacuum:
  - https://github.com/citusdata/pg_cron
  - https://www.postgresql.org/docs/current/sql-vacuum.html
- Scheduler for setting overdue date, and start sql-vacuum
  - https://digon.io/hyd/project/scheduler/t/master/pages/examples/quick_start.html
  - https://digon.io/hyd/project/scheduler/t/master/pages/examples/asyncio.html
- Removed unused packages:
  - https://stackoverflow.com/questions/25376213/delete-unused-packages-from-requirements-file
- Enable HTTPS