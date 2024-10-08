class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///tasks.db'  # SQLiteデータベース
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.gmail.com'  # Gmailを使用
    MAIL_PORT = 587
    MAIL_USE_TLS = True
<<<<<<< HEAD
    MAIL_USERNAME = 'brackpinkfriday@gmail.com'  # 使用するメールアドレス
    MAIL_PASSWORD = 'mldi imdw ebci iwjg'  # アプリパスワードをここに入れる
    MAIL_DEFAULT_SENDER = 'brackpinkfriday@gmial.com'  # 送信者アドレス
=======
    MAIL_USERNAME = 'test@gmail.com'  # 使用するメールアドレス
    MAIL_PASSWORD = 'test'  # アプリパスワードをここに入れる
    MAIL_DEFAULT_SENDER = 'test@gmail.com'  # 送信者アドレス
>>>>>>> 3b780f5d8426fba7337b0a0907236206ace124c9
