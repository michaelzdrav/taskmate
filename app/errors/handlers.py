from app import db
from flask import render_template
from app.errors import bp


@bp.errorhandler(404)
def not_found(error):
    return render_template('errors/404.html', title='Page Not Found'), 404


@bp.errorhandler(500)
def unexpected_error(error):
    db.session.rollback()
    return render_template('errors/500.html', title='Unexpected Error'), 500
