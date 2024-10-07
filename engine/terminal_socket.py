from flask_socketio import SocketIO, emit
import subprocess

class TerminalSocket:
    def __init__(self, app):
        """Инициализируем SocketIO и регистрируем обработчики"""
        self.socketio = SocketIO(app)
        self.register_events()

    def register_events(self):
        """Регистрирует обработчики событий для работы с терминалом"""
        @self.socketio.on('execute_command')
        def handle_command(data):
            command = data.get('command')
            if command:
                try:
                    result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
                    result = result.decode('utf-8')
                except subprocess.CalledProcessError as e:
                    result = f"Error: {e.output.decode('utf-8')}"

                emit('command_result', {'result': result})
    
    def run(self, app, debug=True):
        """Запускает SocketIO сервер."""
        self.socketio.run(app, debug=debug)

# <!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <title>Terminal</title>
#     <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.min.js"></script>
# </head>
# <body>
#     <h1>Terminal</h1>
#     <textarea id="terminal_output" cols="80" rows="20" readonly></textarea><br>
#     <input type="text" id="command_input" placeholder="Enter command">
#     <button id="send_command">Execute</button>

#     <script>
#         const socket = io.connect('http://' + document.domain + ':' + location.port);

#         document.getElementById('send_command').onclick = function() {
#             const command = document.getElementById('command_input').value;
#             socket.emit('execute_command', { command: command });
#         };

#         socket.on('command_result', function(data) {
#             const output = document.getElementById('terminal_output');
#             output.value += data.result + '\n';
#         });
#     </script>
# </body>
# </html>