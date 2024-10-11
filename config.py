class Config:
    SECRET_KEY = 'a_random_string_12345!@#'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///tasks.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Flask-Mailの設定
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = '@gmail.com'
    MAIL_PASSWORD = 'test'  # アプリパスワードをここに入れる
    MAIL_DEFAULT_SENDER = '@gmail.com'