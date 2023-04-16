
# Task Mate
Please make sure to remove the <b>test</b> user in <b>web/db.py</b> if you are going to expose this to the Internet.

Heres a basic to do list to keep you accountable of your tasks. Simply register your own user, create a task with a title, due date and description. 

When your task is overdue, you will see an "Overdue" message displayed, along with an increment of the overdue task counter in the UI. Once completed, move the task to Done. Otherwise, Delete the task to be lost forever.

Each task can have comments made.

Don't expect it to be worked on too much, I really only commit an hour or two a week if I am bored 😃 I just wanted to build this for myself instead of using the Reminders app!

## Features

- Basic Authentication
- Written in Flask
- Basic To Do list
- Easy ability to self host (soon to be dockerised)
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

## Roadmap 
Order depends on what I feel like working on when I have the free time 😃

- Proper logging instead of just printing values everywhere
- Add ability to turn off default user test/test.
- Add settings page, configure timezones, store tasks in local timezones 
- Add delete for comments
- Add edit for comments
- Add get_task before anything that uses the existing task to check it exists
- Refactor create/update to use functions to check due_date 
- add a get_task_comment to every update/delete of comments
- SMTP integration for notifications (task creation/overdue/comments left)
- Introduction of testing using pytests, (#TODO check out https://flask.palletsprojects.com/en/2.2.x/tutorial/tests/)
- CI/CD pipeline to build image and push to Dockerhub
- Deploying this in AWS
  - Deploying in AWS for use
  - Opening up the API for use


## Authors

- [@michaelzdrav](https://www.github.com/michaelzdrav)

## Acknowledgements
- Shout out to Flask tutorial for the frontend. I would have gone for a Bootstrap option but had this old tutorial project saved.

## Screenshots