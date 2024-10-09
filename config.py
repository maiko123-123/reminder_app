class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///tasks.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'brackpinkfriday@gmail.com'
    MAIL_PASSWORD = 'mldi imdw ebci iwjg'  # アプリパスワードをここに入れる
    MAIL_DEFAULT_SENDER = 'brackpinkfriday@gmail.com'


