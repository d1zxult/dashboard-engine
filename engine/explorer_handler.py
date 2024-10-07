import os
from flask import Blueprint, jsonify, request, send_from_directory, abort

class ExplorerHandler:
    def __init__(self, base_dir=None):
        self.base_dir = base_dir or os.path.expanduser('~')

    def _is_path_valid(self, path):
        abs_path = os.path.abspath(path)
        return abs_path.startswith(self.base_dir)
    
    def list_directory(self, path=None):
        """Список файлов и папок в указанной директории."""
        path = path or self.base_dir
        abs_path = os.path.abspath(path)

        if not self._is_path_valid(abs_path):
            abort(403, description='Доступ к этой директории запрещен')

        if os.path.isdir(abs_path):
            try:
                files = os.listdir(abs_path)
                file_list = []
                for f in files:
                    full_path = os.path.join(abs_path, f)
                    file_info = {
                        'name': f,
                        'path': full_path,
                        'is_dir': os.path.isdir(full_path),
                        'size': os.path.getsize(full_path) if os.path.isfile(full_path) else None,
                    }
                    file_list.append(file_info)
                return jsonify({
                    'path': abs_path,
                    'files': file_list
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        else:
            abort(404, description='Директория не найдена')

    def download_file(self, file_path):
        """Скачивание файла."""
        if not file_path:
            abort(400, description='Не указан путь к файлу')
        
        abs_path = os.path.abspath(file_path)
        if not self._is_path_valid(abs_path):
            abort(403, description='Доступ к этому файлу запрещен')

        if os.path.isfile(abs_path):
            directory, filename = os.path.split(abs_path)
            return send_from_directory(directory, filename, as_attachment=True)
        else:
            abort(404, description='Файл не найден')
        
    def go_back(self, path):
        """Переход на одну директорию назад."""
        path = path or self.base_dir
        abs_path = os.path.abspath(path)

        if abs_path == self.base_dir:
            return jsonify({'path': self.base_dir})
        
        parent_dir = os.path.abspath(os.path.join(abs_path, os.pardir))
        return jsonify({'path': parent_dir})

explorer_handler = ExplorerHandler()

explorer_handler_bp = Blueprint('explorer', __name__)

@explorer_handler_bp.route('/api/explorer', methods=['GET'])
def list_directory():
    """Маршрут для получения списка файлов и директорий."""
    path = request.args.get('path')
    return explorer_handler.list_directory(path)

@explorer_handler_bp.route('/api/explorer/download', methods=['GET'])
def download_file():
    """Маршрут для скачивания файла."""
    file_path = request.args.get('file_path')
    return explorer_handler.download_file(file_path)

@explorer_handler_bp.route('/api/explorer/back', methods=['GET'])
def go_back():
    """Маршрут для возврата на уровень вверх в директории."""
    path = request.args.get('path')
    return explorer_handler.go_back(path)

# <!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <title>Linux File Explorer</title>
#     <style>
#         .file-list { margin-top: 20px; }
#         .file-item { margin-bottom: 10px; }
#         .button { margin-right: 10px; }
#     </style>
# </head>
# <body>
#     <h1>File Explorer</h1>

#     <!-- Кнопка назад -->
#     <button onclick="goBack()">Back</button>

#     <div id="file-list" class="file-list"></div>

#     <script>
#         function loadFiles(path = '') {
#             fetch(`/api/explorer?path=${path}`)
#                 .then(response => response.json())
#                 .then(data => {
#                     const fileList = document.getElementById('file-list');
#                     fileList.innerHTML = ''; // Очищаем старый список файлов

#                     // Отображаем текущую директорию
#                     fileList.innerHTML += `<p>Current path: ${data.path}</p>`;

#                     data.files.forEach(file => {
#                         const fileItem = document.createElement('div');
#                         fileItem.classList.add('file-item');

#                         // Если это папка, добавляем ссылку для перехода
#                         if (file.is_dir) {
#                             fileItem.innerHTML = `
#                                 <span class="button">[DIR]</span>
#                                 <a href="#" onclick="loadFiles('${file.path}')">${file.name}</a>
#                             `;
#                         } else {
#                             // Если это файл, добавляем возможность скачать
#                             fileItem.innerHTML = `
#                                 <span class="button">[FILE]</span>
#                                 ${file.name} (${file.size ? file.size + ' bytes' : 'Unknown size'})
#                                 <a href="/api/explorer/download?file_path=${file.path}" class="button">Download</a>
#                             `;
#                         }

#                         fileList.appendChild(fileItem);
#                     });
#                 })
#                 .catch(err => console.error(err));
#         }

#         function goBack() {
#             const currentPath = document.querySelector('p').innerText.replace('Current path: ', '');
#             fetch(`/api/explorer/back?path=${currentPath}`)
#                 .then(response => response.json())
#                 .then(data => {
#                     loadFiles(data.path);
#                 })
#                 .catch(err => console.error(err));
#         }

#         // Загрузка корневой директории при загрузке страницы
#         window.onload = () => {
#             loadFiles();
#         };
#     </script>
# </body>
# </html>