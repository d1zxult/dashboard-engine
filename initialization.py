from flask import render_template
from configuration import create_app

app, font_awesome, terminal_socket, resource_monitor, = create_app() # Create the app and ResourceMonitor instance

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

if __name__ == "__main__":
    terminal_socket.socketio.run(app, host='0.0.0.0', port=5000, debug=True) # Use socketio to run the app with WebSocket support
