from flask import current_app
from twilio.rest import Client


def _get_twilio_verify_client():
    """
    Get the Twilio Verify API client
    """
    return Client(
        current_app.config['TWILIO_ACCOUNT_SID'],
        current_app.config['TWILIO_AUTH_TOKEN']
    ).verify.services(current_app.config['TWILIO_VERIFY_SERVICE_ID'])


def request_email_verification_token(email):
    """Generate a token to be sent to user email"""
    verify = _get_twilio_verify_client()
    verify.verifications.create(to=email, channel='email')


def check_email_verification_token(email, token):
    """Client's token is verified"""
    verify = _get_twilio_verify_client()
    try:
        result = verify.verification_checks.create(to=email, code=token)
        return result.status == 'approved'
    except:
        return False
