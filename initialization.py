from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from engine.resources_handler import ResourcesHandler
from threading import Thread
import time

def create_app():
    app = Flask(__name__, template_folder='app/temp', static_folder='app/static')
    resources_handler = ResourcesHandler()  # Создание экземпляра ResourcesHandler
    return app, resources_handler

app, resources_handler = create_app()
socketio = SocketIO(app)  # Инициализация SocketIO

@app.route('/')
def index():
    return render_template('auth.html')

@app.route('/terminal')
def terminal():
    return render_template('terminal.html')

@app.route('/overview')
def overview():
    return render_template('overview.html')

@app.route('/explorer')
def explorer():
    return render_template('explorer.html')

@app.route('/modules')
def modules():
    return render_template('modules.html')

@app.route('/settings')
def setting():
    return render_template('settings.html')

def send_system_data():
    while True:
        data = resources_handler.get_resource_data()
        socketio.emit('system_data', data)
        time.sleep(1)

thread = Thread(target=send_system_data)
thread.start()

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
