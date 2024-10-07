from flask import Flask
from flask_font_awesome import FontAwesome # Импортируем патч для FontAwesome
from engine.explorer_handler import explorer_handler_bp  # Импортируем blueprint проводника
from engine.resource_monitor import ResourceMonitor  # Импортируем класс ResourceMonitor
from engine.terminal_socket import TerminalSocket # Импортируем класс TerminalSocket

def create_app():
    app = Flask(__name__, template_folder='app/temp', static_folder='app/static') # Создание и конфигурация приложения

    font_awesome = FontAwesome(app) # Инициализация FontAwesome

    terminal_socket = TerminalSocket(app) # Создание экземпляра TerminalSocket

    resource_monitor = ResourceMonitor() # Создание экземпляра ResourceMonitor

    app.register_blueprint(explorer_handler_bp) # Регистрация blueprint проводника

    return app, font_awesome, terminal_socket, resource_monitor
