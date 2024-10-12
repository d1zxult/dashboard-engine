import psutil
import subprocess

class ResourcesHandler:
    def __init__(self):
        self.cpu_percent = None
        self.cpu_cores = None
        self.cpu_threads = None
        self.cpu_freq = None
        self.cpu_temp = None
        self.memory_total = None
        self.memory_used = None
        self.memory_free = None
        self.swap_total = None
        self.swap_used = None
        self.swap_free = None

    def get_system_info(self):
        """Обновляет информацию о загруженности системы и сохраняет в объекте"""
        self.cpu_percent = psutil.cpu_percent(interval=1)
        self.cpu_cores = psutil.cpu_count()
        self.cpu_threads = psutil.cpu_count(logical=False)
        self.cpu_freq = psutil.cpu_freq()
        memory_info = psutil.virtual_memory()
        swap_info = psutil.swap_memory()

        self.memory_total = round(memory_info.total / (1024 ** 2), 1)  # MB
        self.memory_used = round(memory_info.used / (1024 ** 2), 1)    # MB
        self.memory_free = round(memory_info.free / (1024 ** 2), 1)    # MB
        self.swap_total = round(swap_info.total / (1024 ** 2), 1)      # MB
        self.swap_used = round(swap_info.used / (1024 ** 2), 1)        # MB
        self.swap_free = round(swap_info.free / (1024 ** 2), 1)        # MB

    def get_cpu_temp(self):
        """Обновляет информацию о температуре процессора и сохраняет ее в объекте"""
        try:
            output = subprocess.check_output(['sensors']).decode('utf-8')
            for line in output.split('\n'):
                if 'Core' in line or 'Package id' in line:
                    self.cpu_temp = line.strip()
                    break
        except Exception as e:
            print(f'Ошибка get_cpu_temp(): {e}')

    def get_resource_data(self):
        """Получает данные о ресурсах в виде словаря для передачи через WebSocket"""
        self.get_system_info()
        self.get_cpu_temp()

        return {
            'cpu_used': self.cpu_percent,
            'gpu_used': 0,
            'memory_used': round(self.memory_used / self.memory_total * 100) if self.memory_total else 0,
            'swap_used': round(self.swap_used / self.swap_total * 100) if self.swap_total else 0
        }

    def to_dict(self):
        """Возвращает информацию в виде словаря"""
        return {
            'cpu_percent': self.cpu_percent,
            'cpu_cores': self.cpu_cores,
            'cpu_threads': self.cpu_threads,
            'cpu_freq': self.cpu_freq._asdict() if self.cpu_freq else None,
            'cpu_temp': self.cpu_temp,
            'memory_total': self.memory_total,
            'memory_used': self.memory_used,
            'memory_free': self.memory_free,
            'swap_total': self.swap_total,
            'swap_used': self.swap_used,
            'swap_free': self.swap_free
        }
