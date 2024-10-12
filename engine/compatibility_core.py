# TODO Проверка RAID-конфигураций - если используется RAID, можно добавить информацию о его состоянии
# TODO сделать конфиг для записи туда информации, которая не изменяется

import os
import platform
import psutil
import subprocess
import resource
import GPUtil
from datetime import datetime

class SystemInfoHandler:
    def __init__(self):
        self.kernel_version = None
        self.distribution_name = None
        self.package_manager = None
        self.swap_enabled = False
        self.updates_available = False
        self.open_file_limit = None
        self.process_limit = None
        self.current_time = None
        self.gpus_info = []

    def get_kernel_version(self):
        """Получение версии ядра Linux"""
        try:
            self.kernel_version = platform.release()
            return self.kernel_version
        except Exception as e:
            print(f'Ошибка получения версии ядра: {e}')
            return None

    def get_distribution_info(self):
        """Получение информации о дистрибутиве Linux"""
        try:
            # Чтение информации из /etc/os-release
            with open('/etc/os-release') as f:
                lines = f.readlines()
                for line in lines:
                    if line.startswith('NAME='):
                        self.distribution_name = line.split('=')[1].strip().strip('"')
                    # Можно добавить больше полей при необходимости

        except Exception as e:
            print(f'Ошибка получения информации о дистрибутиве: {e}')

    def get_package_manager(self):
        """Определение пакетного менеджера"""
        try:
            if os.path.exists('/usr/bin/apt'):
                self.package_manager = 'apt'
            elif os.path.exists('/usr/bin/dnf'):
                self.package_manager = 'dnf'
            elif os.path.exists('/usr/bin/yum'):
                self.package_manager = 'yum'
            elif os.path.exists('/usr/bin/zypper'):
                self.package_manager = 'zypper'
            elif os.path.exists('/usr/bin/pacman'):
                self.package_manager = 'pacman'
            else:
                self.package_manager = 'Unknown'
                
        except Exception as e:
            print(f'Ошибка определения пакетного менеджера: {e}')

    def check_swap(self):
        """Проверка наличия Swap"""
        swap_info = psutil.swap_memory()
        self.swap_enabled = swap_info.total > 0

    def check_updates(self):
        """Проверка наличия доступных обновлений пакетов"""
        try:
            if self.package_manager == 'apt':
                output = subprocess.check_output(['apt', 'list', '--upgradable']).decode('utf-8')
                self.updates_available = 'upgradable' in output
            elif self.package_manager == 'dnf':
                output = subprocess.check_output(['dnf', 'check-update']).decode('utf-8')
                self.updates_available = 'No packages marked for update' not in output
            elif self.package_manager == 'yum':
                output = subprocess.check_output(['yum', 'check-update']).decode('utf-8')
                self.updates_available = 'No packages marked for Update' not in output
            elif self.package_manager == 'zypper':
                output = subprocess.check_output(['zypper', 'list-updates']).decode('utf-8')
                self.updates_available = 'No updates found' not in output
            elif self.package_manager == 'pacman':
                output = subprocess.check_output(['pacman', '-Qu']).decode('utf-8')
                self.updates_available = bool(output.strip()) # Если не пустой вывод, занчит обновления есть
            else:
                self.updates_available = False

        except Exception as e:
            print(f'Ошибка проверки обновление: {e}')
            self.updates_available = False

    def check_ulimits(self):
        """Проверка лимитов ulimit для открытых файлов и процессов"""
        try:
            self.open_file_limit = resource.getrlimit(resource.RLIMIT_NOFILE)
            self.process_limit = resource.getrlimit(resource.RLIMIT_NPROC)
        except Exception as e:
            print(f'Ошибка проверки ulimit: {e}')
    
    def get_current_server_time(self):
        """Возвращает текущее системное время сервера в читаемом формате."""
        current_time = datetime.now() # Получение текущего времени
        return current_time.strftime('%Y-%m-%d %H:%M:%S')
    
    def check_gpus(self):
        """Проверка наличия доступных GPU и сбор информации о них"""
        gpus = GPUtil.getGPUs()
        if not gpus:
            self.gpus_info.append('N/A')
        else:
            try:
                for gpu in gpus:
                    gpu_info = {
                        'id': gpu.id,
                        'name': gpu.name,
                        'load': gpu.load * 100,
                        'memory_total': gpu.memoryTotal,
                        'memory_free': gpu.memoryFree,
                        'memory_used': gpu.memoryUsed,
                        'temperature': gpu.temperature
                    }
                    self.gpus_info.append(gpu_info)

            except Exception as e:
                print(f'Ошибка проверки GPU: {e}')
                self.gpus_info.append("N/A")

    def to_dict(self):
        """Возвращает информацию о системе в виде словаря"""
        return {
            'kernel_version': self.kernel_version,
            'distribution_name': self.distribution_name,
            'package_manager': self.package_manager,
            'swap_enabled': self.swap_enabled,
            'updates_available': self.updates_available,
            'open_file_limit': {
                'soft_limit': self.open_file_limit[0],  # Мягкий лимит
                'hard_limit': self.open_file_limit[1]   # Жесткий лимит

            },
            'process_limit': {
                'soft_limit': self.process_limit[0],  # Мягкий лимит
                'hard_limit': self.process_limit[1]   # Жесткий лимит
            },
            'current_time': self.current_time,
            'gpus_info': self.gpus_info
        }

class ProcessHandler:
    def __init__(self):
        self.processes_info = []

    def get_processes_info(self):
        """Получение информации о текущих процессах"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
                # Добавляем информацию о каждом процессе в список
                self.processes_info.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'cpu_percent': proc.info['cpu_percent'],
                    'memory_info': proc.info['memory_info']._asdict() # Преобразуем namedtuple в словарь
                })

        except Exception as e:
            print(f'Ошибка получения информации о процессах: {e}')

    def get_top_processes(self, limit=10):
        """Получение информации о топ-N ресурсоемких процессах"""
        # Сортируем по использованию CPU и возвращаем топ процессов
        return sorted(self.processes_info, key=lambda x: x['cpu_percent'], reverse=True)[:limit]

    def to_dict(self):
        """Возвращает информацию о процессах в виде словаря"""
        return {
            'processes_info': self.processes_info
        }


class FileSystemHandler:
    def __init__(self):
        self.file_systems = []

    def check_file_system(self):
        """Получение информации о файловых системах и дисках"""
        partitions = psutil.disk_partitions(all=False)
        for partition in partitions:
            fs_info = {
                'device': partition.device,
                'mountpoint': partition.mountpoint,
                'fstype': partition.fstype,
                'options': partition.opts,
                'disk_type': self.get_disk_type(partition.device)
            }
            self.file_systems.append(fs_info)

    def get_disk_type(self, device):
        """Определение типа диска (SSD или HDD)

        Args:
            device (str): /dev/sdX
        """

        try:
            # Вызов команды lsblk для получния типа устройства
            output = subprocess.check_output(['lsblk', 'd', '-o', 'NAME,ROTA'], text=True).splitlines()
            for line in output[1:]: # Пропускаем заголовок
                parts = line.split()
                name, rota = parts[0], parts[1]
                if f'/dev/{name}' == device:
                    if rota == 0:
                        if 'mmcblk' in device:
                            return 'microSD/eMMC'
                        return 'SSD'
                    else:
                        return 'HDD'
                
        except Exception as e:
            print(f'Ошибка определения типа диска для {device}: {e}')
            return 'Unknown'

    def to_dict(self):
        """Возвращает информацию о файловых системах в виде словаря"""
        return {
            'file_systems': self.file_systems
        }

class NetworkHandler:
    def __init__(self):
        self.active_ipv4 = False
        self.active_ipv6 = False
        self.ipv4_addr = None
        self.ipv6_addr = None
        self.network_interfaces = {}
        

    def check_active_ip_version(self):
        """Проверка активных сетевых интерфейсов с IPv4 и IPv6"""
        interfaces = psutil.net_if_addrs()
        for interface, addrs in interfaces.items():
            for addr in addrs:
                if addr.family == psutil.AF_INET and addr.address != '127.0.0.1': # IPv4, исключая localhost
                    self.active_ipv4 = True
                    self.ipv4_addr = addr.address
                elif addr.family == psutil.AF_INET6 and not addr.address.startswith('::1'): # IPv6, исключая localhost
                    self.active_ipv6 = True
                    self.ipv6_addr = addr.address

    def check_network_interfaces(self):
        """Проверка конфигурации всех доступных сетевых интерфейсов"""
        interfaces = psutil.net_if_stats()
        for interface, stats in interfaces.items():
            self.network_interfaces[interface] = {
                'is_up': stats.isup,
                'mtu': stats.mtu
            }

    def to_dict(self):
        """Возвращает информацию о активных IP версиях в виде словаря"""
        return {
            'active_ipv4': self.active_ipv4,
            'active_ipv6': self.active_ipv6,
            'ipv4_addr': self.ipv4_addr,
            'ipv6_addr': self.ipv6_addr,
            'network_interfaces': self.network_interfaces
        }

class SecurityHandler:
    def __init__(self):
        self.selinux_status = 'Unknown'
        self.apparmor_status = 'Unknown'

    def check_selinux(self):
        """Проверка статуса SELinux"""
        try:
            output = subprocess.check_output(['sestatus'], stderr=subprocess.STDOUT).decode('utf-8')
            if 'enabled' in output:
                self.selinux_status = 'Enabled'
            else:
                self.selinux_status = 'Disabled'

        except FileNotFoundError:
            self.selinux_status = 'not installed'

    def check_apparmor(self):
        """Проверка статуса AppArmor"""
        try:
            output = subprocess.check_output(['apparmor_status'], stderr=subprocess.STDOUT).decode('utf-8')
            if 'profiles are in enforce mode' in output:
                self.apparmor_status = 'Enforcing'
            elif 'profiles are in complain mode' in output:
                self.apparmor_status = 'Complain'
            else:
                self.apparmor_status = 'Disabled'
            
        except Exception as e:
            print(f'Ошибка при проверке AppArmor: {e}')
            self.apparmor_status = 'Not installed'

    def to_dict(self):
        """Возвращает информацию о статусе SELinux и AppArmor в виде словаря"""
        return {
            'selinux_status': self.selinux_status,
            'apparmor_status': self.apparmor_status
        }


class VirtualizationHandler:
    def __init__(self):
        self.kvm_supported = False
        self.docker_installed = False
        self.podman_installed = False

    def check_kvm_support(self):
        """Проверка поддержки KVM"""
        try:
            # Проверяем наличие KVM модуля в /proc/modules
            output = subprocess.check_output(['cat', '/proc/modules']).decode('utf-8')
            if 'kvm' in output:
                self.kvm_supported = True
            else:
                self.kvm_supported = False
        except Exception as e:
            print(f'Ошибка проверки поддержки KVM: {e}')
            self.kvm_supported = False


    def check_docker(self):
        """Проверка наличия Docker на системе"""
        try:
            subprocess.check_output(['docker', '--version'], stderr=subprocess.STDOUT)
            self.docker_installed = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.docker_installed = False

    def check_podman(self):
        """Проверка наличия Podman на системе"""
        try:
            subprocess.check_output(['podman', '--version'], stderr=subprocess.STDOUT)
            self.podman_installed = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.podman_installed = False

    def to_dict(self):
        """Возвращает информацию о наличии Docker и Podman в виде словаря"""
        return {
            'kvm_supported': self.kvm_supported,
            'docker_installed': self.docker_installed,
            'podman_installed': self.podman_installed
        }