class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///tasks.db'  # SQLiteデータベース
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.gmail.com'  # Gmailを使用
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = ''  # 使用するメールアドレス
    MAIL_PASSWORD = ''  # アプリパスワードをここに入れる
    MAIL_DEFAULT_SENDER = ''  # 送信者アドレス
