from flask_mail import Mail, Message
from extensions import mail

def send_reminder_email(recipient, subject, body):
    msg = Message(subject, recipients=[recipient])
    msg.body = body
    try:
        mail.send(msg)
        print(f"Email sent to {recipient} successfully.")
    except Exception as e:
        print(f"Error sending email: {e}")