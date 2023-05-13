# Task Mate
Heres a basic to do list to keep you accountable of your tasks. Simply register your own user, create a task with a title, due date and description. Each task can have comments made.

When your task is overdue, you will see an "Overdue" message displayed, along with an increment of the overdue task counter in the UI. Once completed, move the task to Done. Otherwise, Delete the task to be lost forever.

Please make sure to remove the <b>test</b> user in <b>web/db.py</b> if you are going to expose this to the Internet.

## Features

- Basic Authentication
- Written in Flask
- Basic To Do list
- Easy ability to self host (Docker repo: mz1234/taskmate)
- SQLite database (more options coming)

## Installation

Install Task Mate with the Makefile

```bash
  make install
  make db
```

## Running

Use the Makefile to initialise a database

```bash
  make run
```

Inspecting the database can be done using the Makefile also

```bash
  make db-view
```

## Docker

Run with Docker via repo https://hub.docker.com/r/mz1234/taskmate

```bash
  docker run -d -p 5001:5001 mz1234/taskmate
```

## Testing

Run Pytest against the code, including test coverage

```bash
  make test
```

SMTP testing (catch-all web UI at localhost:1080)

```bash
  sh docker-compose/run.sh
```

## Roadmap 
Order depends on what I feel like working on when I have the free time 😃

- ~~CI/CD pipeline to build image and push to Dockerhub~~ 
- ~~Add pytest coverage (#TODO check out https://github.com/pytest-dev/pytest-cov)~~
- ~~Introduction of testing using pytests, (#TODO check out https://flask.palletsprojects.com/en/2.2.x/tutorial/tests/)~~
- Add advanced pytests ⌛
- SMTP integration for notifications (task creation/overdue/comments left) ⌛
- Proper logging instead of just printing values everywhere
- Add ability to turn off default user test/test.
- Add settings page, configure timezones, store tasks in local timezones 
- Add delete for comments
- Add edit for comments
- Add get_task before anything that uses the existing task to check it exists
- Refactor create/update to use functions to check due_date 
- add a get_task_comment to every update/delete of comments
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
- Deploying this in AWS
  - Deploying in AWS for use
  - Opening up the API for use


## Authors

- [@michaelzdrav](https://www.github.com/michaelzdrav)

## Acknowledgements
- Shout out to Flask tutorial for the frontend. I would have gone for a Bootstrap option but had this old tutorial project saved.

## Screenshots
![](/screenshots/creating-a-task.png)
![](/screenshots/adding-a-comment.png)
![](/screenshots/done-tasks.png)
