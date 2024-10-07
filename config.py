class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///tasks.db'  # SQLiteデータベース
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.gmail.com'  # Gmailを使用
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'your_email@gmail.com'
    MAIL_PASSWORD = 'your_password'
    MAIL_DEFAULT_SENDER = 'your_email@gmail.com'

