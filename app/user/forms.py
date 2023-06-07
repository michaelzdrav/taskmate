from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, DateField
from wtforms.validators import DataRequired, Length
from flask_wtf.file import FileField, FileAllowed


# -----------------------
# Create task
# -----------------------


class CreateTaskForm(FlaskForm):
    """User can create a task"""
    title = StringField(
        'Title',
        validators=[DataRequired(), Length(min=2, max=64)],
        render_kw={'autofocus':True, 'placeholder': 'TaskMate Title'})
    body = TextAreaField(
        'Body',
        validators=[DataRequired()],
        render_kw={'autofocus':True, 'placeholder': 'Markdown enabled'})
    due_date = DateField(
        'Due Date', validators=[DataRequired()])
    file = FileField(
        'Attach File',
        validators=[FileAllowed(['png', 'gif', 'jpg', 'jpeg', 'pdf'], 'PDF and pictures only!')])
    submit = SubmitField('Create')



class TaskCommentForm(FlaskForm):
    """User can add a comment to a task"""
    body = TextAreaField(
        'Body',
        validators=[DataRequired()],
        render_kw={'autofocus':True, 'placeholder': 'Markdown enabled'})
    submit_comment = SubmitField('Create')

# -----------------------
# End of create task
# -----------------------
