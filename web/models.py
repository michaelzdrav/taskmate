from web import db

class Tenant(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, unique=True, nullable=False)
    timezone = db.Column(db.Text, nullable=False, default="UTC")

    def __repr__(self):
        return "<Tenant {}>".format(self.name)

    def get_id(self):
        return self.id


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenant.id"), nullable=False)
    username = db.Column(db.Text, unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return "<User {}>".format(self.username)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenant.id"), nullable=False)
    created = db.Column(
        db.DateTime, nullable=False, server_default=db.func.utc_timestamp()
    )
    due_date = db.Column(db.DateTime, default=None)
    title = db.Column(db.Text, nullable=False)
    status = db.Column(db.Text, nullable=False, default="ACTIVE")
    body = db.Column(db.Text, default=None)
    author = db.relationship("User")
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __repr__(self):
        return "<Task ID {}>".format(self.id)


class TaskComment(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenant.id"), nullable=False)
    task_id = db.Column(
        db.Integer, db.ForeignKey("task.id", ondelete="CASCADE"), nullable=False
    )
    created = db.Column(
        db.DateTime, nullable=False, server_default=db.func.utc_timestamp()
    )
    content = db.Column(db.Text, nullable=False)
    task = db.relationship("Task")

    def __repr__(self):
        return "<Comment ID {}>".format(self.id)
