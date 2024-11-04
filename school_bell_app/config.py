import os

class Config:
    # Секретный ключ для защиты данных сессий
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key'
    
    # Настройки базы данных
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///bells.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Отключение отслеживания изменений
    
    # Папка для загрузки музыкальных файлов
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static/music')
