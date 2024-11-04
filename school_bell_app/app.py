from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_apscheduler import APScheduler
from playsound import playsound
import os
from datetime import datetime
from config import Config  # Импортируйте ваш конфигурационный класс

app = Flask(__name__)
app.config.from_object(Config)  # Загрузка конфигурации из файла

# Инициализация базы данных
db = SQLAlchemy(app)

# Настройка и запуск планировщика задач
scheduler = APScheduler()
scheduler.init_app(app)

# Модель для хранения расписания звонков
class BellSchedule(db.Model):
    __tablename__ = 'bell_schedule'
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    music_file = db.Column(db.String(120), nullable=True)

# Функция для воспроизведения музыки
def play_music(file_path):
    if file_path and os.path.exists(file_path):
        try:
            playsound(file_path)
        except Exception as e:
            print(f"Ошибка воспроизведения: {e}")
    else:
        print("Файл не найден или путь не указан.")

# Маршрут для главной страницы
@app.route('/')
def index():
    schedules = BellSchedule.query.all()
    return render_template('index.html', schedules=schedules)

# Маршрут для добавления расписания звонков
@app.route('/add_bell', methods=['POST'])
def add_bell():
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')
    music_file = request.files.get('music_file')
    
    # Сохраняем загруженную музыку
    if music_file:
        music_path = os.path.join(app.config['UPLOAD_FOLDER'], music_file.filename)
        music_file.save(music_path)
    else:
        music_path = None
    
    # Добавляем запись в базу данных
    new_bell = BellSchedule(
        start_time=datetime.strptime(start_time, '%H:%M').time(),
        end_time=datetime.strptime(end_time, '%H:%M').time(),
        music_file=music_path
    )
    db.session.add(new_bell)
    db.session.commit()
    
    # Планируем задачу для звонков с использованием APScheduler
    scheduler.add_job(id=str(new_bell.id) + "_start", func=play_music, trigger='cron',
                      hour=new_bell.start_time.hour, minute=new_bell.start_time.minute, args=[music_path])
    
    flash("Звонок добавлен!", "success")
    return redirect(url_for('index'))

# Маршрут для удаления расписания
@app.route('/delete_bell/<int:id>', methods=['POST'])
def delete_bell(id):
    bell = BellSchedule.query.get(id)
    if bell:
        db.session.delete(bell)
        db.session.commit()
        # Удаление задачи из планировщика
        scheduler.remove_job(str(bell.id) + "_start")
        flash("Звонок удален!", "success")
    return redirect(url_for('index'))

# Функция для создания базы данных
def setup_database():
    with app.app_context():
        db.create_all()  # Создание всех таблиц в базе данных

if __name__ == '__main__':
    setup_database()  # Инициализация базы данных
    scheduler.start()  # Запуск планировщика после инициализации базы данных
    app.run(debug=True)  # Запуск приложения
