#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SYSTEM MONITOR - Tizim resurslarini kuzatish va Telegram orqali xabar yuborish
Versiya: 1.2.0
"""

import os
import sys
import time
import logging
import configparser
import subprocess
import socket
import platform
import datetime
import requests
import json
import sqlite3
import psutil
from pathlib import Path
import re

# Default configuration values
DEFAULT_CONFIG_FILE = '/etc/memory-monitor/config.conf'
DEFAULT_LOG_FILE = '/var/log/memory_monitor.log'
DEFAULT_THRESHOLD = 80
DEFAULT_INTERVAL = 60
DEFAULT_LOG_LEVEL = 'INFO'

class SystemMonitor:
    def __init__(self, config_file=DEFAULT_CONFIG_FILE):
        self.config_file = config_file
        self.config = self._load_config()
        self._setup_logging()
        self.last_alert_times = {
            'ram': 0,
            'cpu': 0,
            'disk': 0,
            'swap': 0,
            'load': 0,
            'network': 0
        }
        
        self.logger.info(f"Memory monitoring service boshlandi")
        self.logger.info(f"Konfiguratsiya fayli: {self.config_file}")
        self.logger.debug(f"Monitoring sozlamalari: RAM {self.config['threshold']}%, interval {self.config['check_interval']} sek")
        
        # Test Telegram connection at startup
        self.test_telegram_connection()
        
        # Initialize database if enabled
        if self.config['db_enabled']:
            self._init_database()
        
        # Initialize Prometheus if enabled
        if self.config['prometheus_enabled']:
            self._init_prometheus()

    def _load_config(self):
        default_config = {
            'bot_token': "7120243579:AAEoaMz5DK8pv1uvwmbD--Mmt8nqbhL_mec",
            'chat_id': "664131109",
            'log_file': DEFAULT_LOG_FILE,
            'threshold': DEFAULT_THRESHOLD,
            'check_interval': DEFAULT_INTERVAL,
            'log_level': DEFAULT_LOG_LEVEL,
            'alert_message_title': "🖥️ SYSTEM STATUS ALERT",
            'include_top_processes': True,
            'top_processes_count': 10,
            'monitor_cpu': True,
            'cpu_threshold': 90,
            'monitor_disk': True,
            'disk_threshold': 90,
            'disk_path': "/",
            'monitor_swap': True,
            'swap_threshold': 80,
            'monitor_load': True,
            'load_threshold': 5,
            'monitor_network': True,
            'network_interface': "",
            'network_threshold': 90,
            # Database integration settings
            'db_enabled': False,
            'db_type': "sqlite",  # sqlite, mysql, postgresql
            'db_path': "/var/lib/memory-monitor/metrics.db",
            'db_host': "localhost",
            'db_port': 3306,
            'db_name': "system_monitor",
            'db_user': "",
            'db_password': "",
            # Prometheus integration settings
            'prometheus_enabled': False,
            'prometheus_port': 9090,
                # Alert format settings
                # 'alert_format_enabled': True,
                # 'alert_format_top_border': "┌────────────────────────────────────────────┐",
                # 'alert_format_title_border': "├────────────────────────────────────────────┤",
                # 'alert_format_section_border': "├────────────────────────────────────────────┤",
                # 'alert_format_bottom_border': "└────────────────────────────────────────────┘",
                # 'alert_format_line_prefix': "│ ",
                # 'alert_format_line_suffix': " │",
                # 'alert_format_date_emoji': "🗓️",
                # 'alert_format_ram_emoji': "🧠",
                # 'alert_format_cpu_emoji': "🔥",
                # 'alert_format_disk_emoji': "💾",
                # 'alert_format_top_processes_emoji': "🧾",
                # 'alert_format_disk_breakdown_emoji': "📁",
                # 'alert_format_hostname_emoji': "",
                # 'alert_format_ip_emoji': "",
                # 'alert_format_uptime_emoji': "",
                # 'alert_format_os_emoji': "",
                # 'alert_format_kernel_emoji': "",
                # 'alert_format_use_box_drawing': True,
                # 'alert_format_width': 44,
                # 'alert_format_title_align': "center",  # left, center, right
                # 'alert_format_include_system_info': True,
                # 'alert_format_include_resources': True,
                # 'alert_format_include_top_processes': True,
                # 'alert_format_include_disk_breakdown': True
                
                'alert_format_enabled': True,
                'alert_format_use_box_drawing': False,  # ❗ oddiy text uslubi
                'alert_format_title_align': "left",     # chapdan joylashsin
                'alert_format_width': 0,                # kenglikka cheklov yo‘q

                # Emojilar
                'alert_format_date_emoji': "📅",
                'alert_format_ram_emoji': "💥",   # yoki 🧠
                'alert_format_cpu_emoji': "💥",   # yoki 🔥
                'alert_format_disk_emoji': "💥",  # yoki 💾
                'alert_format_top_processes_emoji': "🔍",
                'alert_format_disk_breakdown_emoji': "🔍",  # yoki 📁
                'alert_format_hostname_emoji': "🖥️",
                'alert_format_ip_emoji': "🌐",
                'alert_format_uptime_emoji': "",
                'alert_format_os_emoji': "",
                'alert_format_kernel_emoji': "",

                # Tizim qismlarini ko‘rsatish
                'alert_format_include_system_info': True,
                'alert_format_include_resources': True,
                'alert_format_include_top_processes': True,
                'alert_format_include_disk_breakdown': True,

        }

        try:
            if not os.path.exists(self.config_file):
                self.logger.error(f"XATO: Konfiguratsiya fayli topilmadi: {self.config_file}")
                self.logger.error("Standart konfiguratsiya qiymatlari ishlatiladi.")
                return default_config

            config = configparser.ConfigParser()
            config.read(self.config_file)
            
            # Map INI sections to our config dictionary
            result = default_config.copy()
            
            # General settings
            if 'General' in config:
                if 'bot_token' in config['General']:
                    result['bot_token'] = config['General']['bot_token']
                if 'chat_id' in config['General']:
                    result['chat_id'] = config['General']['chat_id']
                if 'log_file' in config['General']:
                    result['log_file'] = config['General']['log_file']
                if 'log_level' in config['General']:
                    result['log_level'] = config['General']['log_level'].upper()
                if 'alert_message_title' in config['General']:
                    result['alert_message_title'] = config['General']['alert_message_title']
                
                if 'threshold' in config['General']:
                    result['threshold'] = int(config['General']['threshold'])
                if 'check_interval' in config['General']:
                    result['check_interval'] = int(config['General']['check_interval'])
                if 'top_processes_count' in config['General']:
                    result['top_processes_count'] = int(config['General']['top_processes_count'])
                
                if 'include_top_processes' in config['General']:
                    result['include_top_processes'] = config['General'].getboolean('include_top_processes')
            
            # CPU monitoring
            if 'CPU' in config:
                if 'monitor_cpu' in config['CPU']:
                    result['monitor_cpu'] = config['CPU'].getboolean('monitor_cpu')
                if 'cpu_threshold' in config['CPU']:
                    result['cpu_threshold'] = int(config['CPU']['cpu_threshold'])
            
            # Disk monitoring
            if 'Disk' in config:
                if 'monitor_disk' in config['Disk']:
                    result['monitor_disk'] = config['Disk'].getboolean('monitor_disk')
                if 'disk_threshold' in config['Disk']:
                    result['disk_threshold'] = int(config['Disk']['disk_threshold'])
                if 'disk_path' in config['Disk']:
                    result['disk_path'] = config['Disk']['disk_path']
            
            # Swap monitoring
            if 'Swap' in config:
                if 'monitor_swap' in config['Swap']:
                    result['monitor_swap'] = config['Swap'].getboolean('monitor_swap')
                if 'swap_threshold' in config['Swap']:
                    result['swap_threshold'] = int(config['Swap']['swap_threshold'])
            
            # Load monitoring
            if 'Load' in config:
                if 'monitor_load' in config['Load']:
                    result['monitor_load'] = config['Load'].getboolean('monitor_load')
                if 'load_threshold' in config['Load']:
                    result['load_threshold'] = int(config['Load']['load_threshold'])
            
            # Network monitoring
            if 'Network' in config:
                if 'monitor_network' in config['Network']:
                    result['monitor_network'] = config['Network'].getboolean('monitor_network')
                if 'network_interface' in config['Network']:
                    result['network_interface'] = config['Network']['network_interface']
                if 'network_threshold' in config['Network']:
                    result['network_threshold'] = int(config['Network']['network_threshold'])
            
            # Database integration
            if 'Database' in config:
                if 'db_enabled' in config['Database']:
                    result['db_enabled'] = config['Database'].getboolean('db_enabled')
                if 'db_type' in config['Database']:
                    result['db_type'] = config['Database']['db_type'].lower()
                if 'db_path' in config['Database']:
                    result['db_path'] = config['Database']['db_path']
                if 'db_host' in config['Database']:
                    result['db_host'] = config['Database']['db_host']
                if 'db_name' in config['Database']:
                    result['db_name'] = config['Database']['db_name']
                if 'db_user' in config['Database']:
                    result['db_user'] = config['Database']['db_user']
                if 'db_password' in config['Database']:
                    result['db_password'] = config['Database']['db_password']
                if 'db_port' in config['Database']:
                    result['db_port'] = int(config['Database']['db_port'])
            
            # Prometheus integration
            if 'Prometheus' in config:
                if 'prometheus_enabled' in config['Prometheus']:
                    result['prometheus_enabled'] = config['Prometheus'].getboolean('prometheus_enabled')
                if 'prometheus_port' in config['Prometheus']:
                    result['prometheus_port'] = int(config['Prometheus']['prometheus_port'])
            
            # Alert format settings
            if 'AlertFormat' in config:
                if 'alert_format_enabled' in config['AlertFormat']:
                    result['alert_format_enabled'] = config['AlertFormat'].getboolean('alert_format_enabled')
                if 'alert_format_top_border' in config['AlertFormat']:
                    result['alert_format_top_border'] = config['AlertFormat']['alert_format_top_border']
                if 'alert_format_title_border' in config['AlertFormat']:
                    result['alert_format_title_border'] = config['AlertFormat']['alert_format_title_border']
                if 'alert_format_section_border' in config['AlertFormat']:
                    result['alert_format_section_border'] = config['AlertFormat']['alert_format_section_border']
                if 'alert_format_bottom_border' in config['AlertFormat']:
                    result['alert_format_bottom_border'] = config['AlertFormat']['alert_format_bottom_border']
                if 'alert_format_line_prefix' in config['AlertFormat']:
                    result['alert_format_line_prefix'] = config['AlertFormat']['alert_format_line_prefix']
                if 'alert_format_line_suffix' in config['AlertFormat']:
                    result['alert_format_line_suffix'] = config['AlertFormat']['alert_format_line_suffix']
                if 'alert_format_date_emoji' in config['AlertFormat']:
                    result['alert_format_date_emoji'] = config['AlertFormat']['alert_format_date_emoji']
                if 'alert_format_ram_emoji' in config['AlertFormat']:
                    result['alert_format_ram_emoji'] = config['AlertFormat']['alert_format_ram_emoji']
                if 'alert_format_cpu_emoji' in config['AlertFormat']:
                    result['alert_format_cpu_emoji'] = config['AlertFormat']['alert_format_cpu_emoji']
                if 'alert_format_disk_emoji' in config['AlertFormat']:
                    result['alert_format_disk_emoji'] = config['AlertFormat']['alert_format_disk_emoji']
                if 'alert_format_top_processes_emoji' in config['AlertFormat']:
                    result['alert_format_top_processes_emoji'] = config['AlertFormat']['alert_format_top_processes_emoji']
                if 'alert_format_disk_breakdown_emoji' in config['AlertFormat']:
                    result['alert_format_disk_breakdown_emoji'] = config['AlertFormat']['alert_format_disk_breakdown_emoji']
                if 'alert_format_hostname_emoji' in config['AlertFormat']:
                    result['alert_format_hostname_emoji'] = config['AlertFormat']['alert_format_hostname_emoji']
                if 'alert_format_ip_emoji' in config['AlertFormat']:
                    result['alert_format_ip_emoji'] = config['AlertFormat']['alert_format_ip_emoji']
                if 'alert_format_uptime_emoji' in config['AlertFormat']:
                    result['alert_format_uptime_emoji'] = config['AlertFormat']['alert_format_uptime_emoji']
                if 'alert_format_os_emoji' in config['AlertFormat']:
                    result['alert_format_os_emoji'] = config['AlertFormat']['alert_format_os_emoji']
                if 'alert_format_kernel_emoji' in config['AlertFormat']:
                    result['alert_format_kernel_emoji'] = config['AlertFormat']['alert_format_kernel_emoji']
                if 'alert_format_use_box_drawing' in config['AlertFormat']:
                    result['alert_format_use_box_drawing'] = config['AlertFormat'].getboolean('alert_format_use_box_drawing')
                if 'alert_format_width' in config['AlertFormat']:
                    result['alert_format_width'] = int(config['AlertFormat']['alert_format_width'])
                if 'alert_format_title_align' in config['AlertFormat']:
                    result['alert_format_title_align'] = config['AlertFormat']['alert_format_title_align'].lower()
                if 'alert_format_include_system_info' in config['AlertFormat']:
                    result['alert_format_include_system_info'] = config['AlertFormat'].getboolean('alert_format_include_system_info')
                if 'alert_format_include_resources' in config['AlertFormat']:
                    result['alert_format_include_resources'] = config['AlertFormat'].getboolean('alert_format_include_resources')
                if 'alert_format_include_top_processes' in config['AlertFormat']:
                    result['alert_format_include_top_processes'] = config['AlertFormat'].getboolean('alert_format_include_top_processes')
                if 'alert_format_include_disk_breakdown' in config['AlertFormat']:
                    result['alert_format_include_disk_breakdown'] = config['AlertFormat'].getboolean('alert_format_include_disk_breakdown')
            
            # Validate required settings
            if not result['bot_token'] or not result['chat_id']:
                print("XATO: BOT_TOKEN va CHAT_ID konfiguratsiya faylida ko'rsatilishi kerak.")
                sys.exit(1)
            
            # Set default network interface if not specified
            if not result['network_interface']:
                interfaces = psutil.net_if_addrs()
                for iface in interfaces:
                    if iface != 'lo':
                        result['network_interface'] = iface
                        break
            
            return result
            
        except Exception as e:
            print(f"Konfiguratsiya faylini o'qishda xatolik: {e}")
            print("Standart konfiguratsiya qiymatlari ishlatiladi.")
            return default_config

    def _setup_logging(self):
        log_levels = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR
        }
        
        # Create log directory if it doesn't exist
        log_dir = os.path.dirname(self.config['log_file'])
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        # Configure logging
        log_level = log_levels.get(self.config['log_level'], logging.INFO)
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - [%(levelname)s] - %(message)s',
            handlers=[
                logging.FileHandler(self.config['log_file']),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('memory_monitor')

    def _init_database(self):
        try:
            db_type = self.config['db_type']
            self.logger.info(f"Ma'lumotlar bazasi integratsiyasi yoqilgan: {db_type}")
            
            if db_type == 'sqlite':
                # Create directory if it doesn't exist
                db_dir = os.path.dirname(self.config['db_path'])
                if db_dir and not os.path.exists(db_dir):
                    os.makedirs(db_dir, exist_ok=True)
                
                # Connect to SQLite database
                self.db_conn = sqlite3.connect(self.config['db_path'])
                self.db_cursor = self.db_conn.cursor()
                
                # Create tables if they don't exist
                self.db_cursor.execute('''
                    CREATE TABLE IF NOT EXISTS metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME NOT NULL,
                        hostname TEXT NOT NULL,
                        ip_address TEXT NOT NULL,
                        ram_usage REAL,
                        cpu_usage REAL,
                        disk_usage REAL,
                        swap_usage REAL,
                        load_average REAL,
                        network_rx REAL,
                        network_tx REAL,
                        extra_data TEXT
                    )
                ''')
                
                self.db_cursor.execute('''
                    CREATE TABLE IF NOT EXISTS alerts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME NOT NULL,
                        hostname TEXT NOT NULL,
                        alert_type TEXT NOT NULL,
                        value TEXT NOT NULL,
                        message TEXT,
                        sent_successfully BOOLEAN
                    )
                ''')
                
                self.db_conn.commit()
                self.logger.info("SQLite ma'lumotlar bazasi muvaffaqiyatli ishga tushirildi")
                
            elif db_type == 'mysql':
                try:
                    import mysql.connector
                    self.db_conn = mysql.connector.connect(
                        host=self.config['db_host'],
                        port=self.config['db_port'],
                        user=self.config['db_user'],
                        password=self.config['db_password'],
                        database=self.config['db_name']
                    )
                    self.db_cursor = self.db_conn.cursor()
                    
                    # Create tables if they don't exist
                    self.db_cursor.execute('''
                        CREATE TABLE IF NOT EXISTS metrics (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            timestamp DATETIME NOT NULL,
                            hostname VARCHAR(255) NOT NULL,
                            ip_address VARCHAR(45) NOT NULL,
                            ram_usage FLOAT,
                            cpu_usage FLOAT,
                            disk_usage FLOAT,
                            swap_usage FLOAT,
                            load_average FLOAT,
                            network_rx FLOAT,
                            network_tx FLOAT,
                            extra_data TEXT
                        )
                    ''')
                    
                    self.db_cursor.execute('''
                        CREATE TABLE IF NOT EXISTS alerts (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            timestamp DATETIME NOT NULL,
                            hostname VARCHAR(255) NOT NULL,
                            alert_type VARCHAR(50) NOT NULL,
                            value VARCHAR(100) NOT NULL,
                            message TEXT,
                            sent_successfully BOOLEAN
                        )
                    ''')
                    
                    self.db_conn.commit()
                    self.logger.info("MySQL ma'lumotlar bazasi muvaffaqiyatli ishga tushirildi")
                    
                except ImportError:
                    self.logger.error("MySQL-connector-python o'rnatilmagan. 'pip install mysql-connector-python' buyrug'i bilan o'rnating.")
                    self.config['db_enabled'] = False
                
            elif db_type == 'postgresql':
                try:
                    import psycopg2
                    self.db_conn = psycopg2.connect(
                        host=self.config['db_host'],
                        port=self.config['db_port'],
                        user=self.config['db_user'],
                        password=self.config['db_password'],
                        database=self.config['db_name']
                    )
                    self.db_cursor = self.db_conn.cursor()
                    
                    # Create tables if they don't exist
                    self.db_cursor.execute('''
                        CREATE TABLE IF NOT EXISTS metrics (
                            id SERIAL PRIMARY KEY,
                            timestamp TIMESTAMP NOT NULL,
                            hostname VARCHAR(255) NOT NULL,
                            ip_address VARCHAR(45) NOT NULL,
                            ram_usage FLOAT,
                            cpu_usage FLOAT,
                            disk_usage FLOAT,
                            swap_usage FLOAT,
                            load_average FLOAT,
                            network_rx FLOAT,
                            network_tx FLOAT,
                            extra_data TEXT
                        )
                    ''')
                    
                    self.db_cursor.execute('''
                        CREATE TABLE IF NOT EXISTS alerts (
                            id SERIAL PRIMARY KEY,
                            timestamp TIMESTAMP NOT NULL,
                            hostname VARCHAR(255) NOT NULL,
                            alert_type VARCHAR(50) NOT NULL,
                            value VARCHAR(100) NOT NULL,
                            message TEXT,
                            sent_successfully BOOLEAN
                        )
                    ''')
                    
                    self.db_conn.commit()
                    self.logger.info("PostgreSQL ma'lumotlar bazasi muvaffaqiyatli ishga tushirildi")
                    
                except ImportError:
                    self.logger.error("Psycopg2 o'rnatilmagan. 'pip install psycopg2-binary' buyrug'i bilan o'rnating.")
                    self.config['db_enabled'] = False
                
            else:
                self.logger.error(f"Noma'lum ma'lumotlar bazasi turi: {db_type}")
                self.config['db_enabled'] = False
                
        except Exception as e:
            self.logger.error(f"Ma'lumotlar bazasini ishga tushirishda xatolik: {e}")
            self.config['db_enabled'] = False

    def _init_prometheus(self):
        try:
            from prometheus_client import start_http_server, Gauge, Counter
            
            # Create metrics
            self.prom_ram_usage = Gauge('system_monitor_ram_usage_percent', 'RAM usage in percent')
            self.prom_cpu_usage = Gauge('system_monitor_cpu_usage_percent', 'CPU usage in percent')
            self.prom_disk_usage = Gauge('system_monitor_disk_usage_percent', 'Disk usage in percent')
            self.prom_swap_usage = Gauge('system_monitor_swap_usage_percent', 'Swap usage in percent')
            self.prom_load_average = Gauge('system_monitor_load_average', 'System load average')
            self.prom_network_rx = Gauge('system_monitor_network_rx_mbps', 'Network receive rate in Mbps')
            self.prom_network_tx = Gauge('system_monitor_network_tx_mbps', 'Network transmit rate in Mbps')
            
            # Create alert counters
            self.prom_ram_alerts = Counter('system_monitor_ram_alerts_total', 'Total number of RAM alerts')
            self.prom_cpu_alerts = Counter('system_monitor_cpu_alerts_total', 'Total number of CPU alerts')
            self.prom_disk_alerts = Counter('system_monitor_disk_alerts_total', 'Total number of disk alerts')
            self.prom_swap_alerts = Counter('system_monitor_swap_alerts_total', 'Total number of swap alerts')
            self.prom_load_alerts = Counter('system_monitor_load_alerts_total', 'Total number of load alerts')
            self.prom_network_alerts = Counter('system_monitor_network_alerts_total', 'Total number of network alerts')
            
            # Start server
            start_http_server(self.config['prometheus_port'])
            self.logger.info(f"Prometheus exporter ishga tushirildi, port: {self.config['prometheus_port']}")
            
        except ImportError:
            self.logger.error("Prometheus-client o'rnatilmagan. 'pip install prometheus-client' buyrug'i bilan o'rnating.")
            self.config['prometheus_enabled'] = False
        except Exception as e:
            self.logger.error(f"Prometheus exporterni ishga tushirishda xatolik: {e}")
            self.config['prometheus_enabled'] = False

    def get_system_info(self):
        hostname = socket.gethostname()
        server_ip = '127.0.0.1'
        
        # Get more detailed IP if available
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            server_ip = s.getsockname()[0]
            s.close()
        except:
            pass
        
        kernel = platform.release()
        os_info = f"{platform.system()} {platform.release()}"
        
        try:
            os_info = subprocess.check_output("cat /etc/os-release | grep PRETTY_NAME | cut -d= -f2 | tr -d '\"'", shell=True).decode().strip()
        except:
            pass
        
        # Get uptime
        uptime_seconds = 0
        try:
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.readline().split()[0])
        except:
            uptime_seconds = time.time() - psutil.boot_time()
        
        uptime_days = int(uptime_seconds // 86400)
        uptime_hours = int((uptime_seconds % 86400) // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)
        
        if uptime_days > 0:
            uptime = f"{uptime_days}d {uptime_hours}h {uptime_minutes}m"
        elif uptime_hours > 0:
            uptime = f"{uptime_hours}h {uptime_minutes}m"
        else:
            uptime = f"{uptime_minutes}m"
        
        # Get CPU info
        cpu_info = "Unknown CPU"
        cpu_cores = psutil.cpu_count(logical=True)
        try:
            with open('/proc/cpuinfo', 'r') as f:
                for line in f:
                    if line.startswith('model name'):
                        cpu_info = line.split(':', 1)[1].strip()
                        break
        except:
            pass
        
        # Get memory info
        total_memory = psutil.virtual_memory().total
        total_memory_gb = total_memory / (1024 ** 3)
        
        # Get disk info
        total_disk = 0
        try:
            disk_usage = psutil.disk_usage(self.config['disk_path'])
            total_disk = disk_usage.total
        except:
            pass
        
        total_disk_gb = total_disk / (1024 ** 3)
        
        return {
            'hostname': hostname,
            'ip': server_ip,
            'os': os_info,
            'kernel': kernel,
            'cpu': f"{cpu_info} ({cpu_cores} cores)",
            'uptime': uptime,
            'total_ram': f"{total_memory_gb:.1f}Gi",
            'total_disk': f"{total_disk_gb:.1f}G"
        }

    def check_ram_usage(self):
        mem = psutil.virtual_memory()
        return mem.percent

    def check_cpu_usage(self):
        if not self.config['monitor_cpu']:
            return 0
        
        return psutil.cpu_percent(interval=1)

    def check_disk_usage(self):
        if not self.config['monitor_disk']:
            return 0
        
        try:
            disk_usage = psutil.disk_usage(self.config['disk_path'])
            return disk_usage.percent
        except Exception as e:
            self.logger.error(f"Disk foydalanishini tekshirishda xatolik: {e}")
            return 0

    def check_swap_usage(self):
        if not self.config['monitor_swap']:
            return 0
        
        try:
            swap = psutil.swap_memory()
            if swap.total == 0:
                return 0
            return swap.percent
        except Exception as e:
            self.logger.error(f"Swap foydalanishini tekshirishda xatolik: {e}")
            return 0

    def check_load_average(self):
        if not self.config['monitor_load']:
            return 0
        
        try:
            load_avg = psutil.getloadavg()[0]  # 1 minute load average
            cpu_cores = psutil.cpu_count(logical=True)
            load_per_core = load_avg / cpu_cores
            
            return load_per_core * 100  # Convert to percentage for threshold comparison
        except Exception as e:
            self.logger.error(f"Load average tekshirishda xatolik: {e}")
            return 0

    def check_network_usage(self):
        if not self.config['monitor_network']:
            return [0, 0]
        
        interface = self.config['network_interface']
        
        try:
            # Get initial counters
            net_io_counters = psutil.net_io_counters(pernic=True)
            if interface not in net_io_counters:
                self.logger.error(f"Tarmoq interfeysi topilmadi: {interface}")
                return [0, 0]
            
            rx_bytes_1 = net_io_counters[interface].bytes_recv
            tx_bytes_1 = net_io_counters[interface].bytes_sent
            
            # Wait 1 second
            time.sleep(1)
            
            # Get counters again
            net_io_counters = psutil.net_io_counters(pernic=True)
            rx_bytes_2 = net_io_counters[interface].bytes_recv
            tx_bytes_2 = net_io_counters[interface].bytes_sent
            
            # Calculate rates in Mbps
            rx_rate = ((rx_bytes_2 - rx_bytes_1) * 8) / 1024 / 1024  # Convert to Mbps
            tx_rate = ((tx_bytes_2 - tx_bytes_1) * 8) / 1024 / 1024  # Convert to Mbps
            
            return [rx_rate, tx_rate]
        except Exception as e:
            self.logger.error(f"Tarmoq foydalanishini tekshirishda xatolik: {e}")
            return [0, 0]

    def get_top_processes(self, resource_type):
        count = self.config['top_processes_count']
        
        try:
            if resource_type == 'RAM':
                processes = []
                for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
                    try:
                        processes.append((proc.info['pid'], proc.info['name'], proc.info['memory_percent']))
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        pass
                
                # Sort by memory usage (descending)
                processes.sort(key=lambda x: x[2], reverse=True)
                
                # Format the output
                result = []
                for i, (pid, name, mem_percent) in enumerate(processes[:count]):
                    result.append(f"  - {name.ljust(15)} ({mem_percent:.1f}%)")
                
                return "\n".join(result)
                
            elif resource_type == 'CPU':
                processes = []
                for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                    try:
                        proc.cpu_percent(interval=0.1)  # First call returns 0
                        processes.append((proc.info['pid'], proc.info['name'], proc.info['cpu_percent']))
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        pass
                
                # Sort by CPU usage (descending)
                processes.sort(key=lambda x: x[2], reverse=True)
                
                # Format the output
                result = []
                for i, (pid, name, cpu_percent) in enumerate(processes[:count]):
                    result.append(f"  - {name.ljust(15)} ({cpu_percent:.1f}%)")
                
                return "\n".join(result)
                
            elif resource_type == 'Disk':
                try:
                    output = subprocess.check_output(f"du -h {self.config['disk_path']}/* 2>/dev/null | sort -rh | head -n {count}", shell=True).decode()
                    lines = output.strip().split('\n')
                    result = []
                    for line in lines:
                        if line:
                            parts = line.split('\t')
                            if len(parts) == 2:
                                size, path = parts
                                path = os.path.basename(path)
                                result.append(f"  - /{path.ljust(15)} {size}")
                    return "\n".join(result)
                except:
                    return "Could not get disk usage information"
                
            else:
                return f"Unknown resource type: {resource_type}"
                
        except Exception as e:
            self.logger.error(f"Top jarayonlarni olishda xatolik: {e}")
            return f"Could not get {resource_type} process information"

    def format_alert_message(self, alert_type, usage_value):
        """
        Format alert message according to configuration settings
        """
        if not self.config['alert_format_enabled']:
            # Use simple text format if custom formatting is disabled
            date_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            system_info = self.get_system_info()
            
            message = f"{self.config['alert_message_title']}\n\n"
            message += f"Date: {date_str}\n"
            message += f"Hostname: {system_info['hostname']}\n"
            message += f"IP Address: {system_info['ip']}\n"
            message += f"Uptime: {system_info['uptime']}\n"
            message += f"OS: {system_info['os']}\n"
            message += f"Kernel: {system_info['kernel']}\n\n"
            
            # Get current resource usage
            ram_usage = self.check_ram_usage()
            cpu_usage = self.check_cpu_usage() if self.config['monitor_cpu'] else 0
            disk_usage = self.check_disk_usage() if self.config['monitor_disk'] else 0
            
            message += f"RAM Usage: {ram_usage}% of {system_info['total_ram']}\n"
            message += f"CPU Usage: {cpu_usage}%\n"
            message += f"Disk Usage: {disk_usage}% of {system_info['total_disk']}\n\n"
            
            # Add top processes if enabled
            if self.config['include_top_processes']:
                message += f"Top RAM Consumers:\n{self.get_top_processes('RAM')}\n\n"
                message += f"Disk Usage Breakdown:\n{self.get_top_processes('Disk')}"
            
            return message
        
        # Use custom box format
        width = self.config['alert_format_width']
        line_prefix = self.config['alert_format_line_prefix']
        line_suffix = self.config['alert_format_line_suffix']
        
        # Get system info and resource usage
        date_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        system_info = self.get_system_info()
        ram_usage = self.check_ram_usage()
        cpu_usage = self.check_cpu_usage() if self.config['monitor_cpu'] else 0
        disk_usage = self.check_disk_usage() if self.config['monitor_disk'] else 0
        
        # Format title according to alignment
        title = self.config['alert_message_title']
        title_align = self.config['alert_format_title_align']
        content_width = width - len(line_prefix) - len(line_suffix)
        
        if title_align == 'center':
            title_line = line_prefix + title.center(content_width) + line_suffix
        elif title_align == 'right':
            title_line = line_prefix + title.rjust(content_width) + line_suffix
        else:  # left align
            title_line = line_prefix + title.ljust(content_width) + line_suffix
        
        # Start building the message
        message = []
        message.append(self.config['alert_format_top_border'])
        message.append(title_line)
        message.append(self.config['alert_format_title_border'])
        
        # Add system info section if enabled
        if self.config['alert_format_include_system_info']:
            date_emoji = self.config['alert_format_date_emoji']
            hostname_emoji = self.config['alert_format_hostname_emoji']
            ip_emoji = self.config['alert_format_ip_emoji']
            uptime_emoji = self.config['alert_format_uptime_emoji']
            os_emoji = self.config['alert_format_os_emoji']
            kernel_emoji = self.config['alert_format_kernel_emoji']
            
            message.append(f"{line_prefix}{date_emoji} Date:       {date_str}{' ' * (content_width - len(date_emoji) - len(' Date:       ') - len(date_str))}{line_suffix}")
            message.append(f"{line_prefix}{hostname_emoji} Hostname:     {system_info['hostname']}{' ' * (content_width - len(hostname_emoji) - len(' Hostname:     ') - len(system_info['hostname']))}{line_suffix}")
            message.append(f"{line_prefix}{ip_emoji} IP Address:   {system_info['ip']}{' ' * (content_width - len(ip_emoji) - len(' IP Address:   ') - len(system_info['ip']))}{line_suffix}")
            message.append(f"{line_prefix}{uptime_emoji} Uptime:       {system_info['uptime']}{' ' * (content_width - len(uptime_emoji) - len(' Uptime:       ') - len(system_info['uptime']))}{line_suffix}")
            message.append(f"{line_prefix}{os_emoji} OS:           {system_info['os']}{' ' * (content_width - len(os_emoji) - len(' OS:           ') - len(system_info['os']))}{line_suffix}")
            message.append(f"{line_prefix}{kernel_emoji} Kernel:       {system_info['kernel']}{' ' * (content_width - len(kernel_emoji) - len(' Kernel:       ') - len(system_info['kernel']))}{line_suffix}")
            message.append(self.config['alert_format_section_border'])
        
        # Add resource usage section if enabled
        if self.config['alert_format_include_resources']:
            ram_emoji = self.config['alert_format_ram_emoji']
            cpu_emoji = self.config['alert_format_cpu_emoji']
            disk_emoji = self.config['alert_format_disk_emoji']
            
            ram_text = f"{ram_emoji} RAM Usage:       {ram_usage}% of {system_info['total_ram']}"
            cpu_text = f"{cpu_emoji} CPU Usage:       {cpu_usage}%"
            disk_text = f"{disk_emoji} Disk Usage:      {disk_usage}% of {system_info['total_disk']}"
            
            message.append(f"{line_prefix}{ram_text}{' ' * (content_width - len(ram_text))}{line_suffix}")
            message.append(f"{line_prefix}{cpu_text}{' ' * (content_width - len(cpu_text))}{line_suffix}")
            message.append(f"{line_prefix}{disk_text}{' ' * (content_width - len(disk_text))}{line_suffix}")
            message.append(self.config['alert_format_section_border'])
        
        # Add top processes section if enabled
        if self.config['alert_format_include_top_processes'] and self.config['include_top_processes']:
            top_processes_emoji = self.config['alert_format_top_processes_emoji']
            top_processes_header = f"{top_processes_emoji} Top RAM Consumers:"
            message.append(f"{line_prefix}{top_processes_header}{' ' * (content_width - len(top_processes_header))}{line_suffix}")
            
            top_processes = self.get_top_processes('RAM').split('\n')[:3]  # Limit to 3 processes
            for proc in top_processes:
                message.append(f"{line_prefix}{proc}{' ' * (content_width - len(proc))}{line_suffix}")
            
            message.append(self.config['alert_format_section_border'])
        
        # Add disk breakdown section if enabled
        if self.config['alert_format_include_disk_breakdown'] and self.config['include_top_processes']:
            disk_breakdown_emoji = self.config['alert_format_disk_breakdown_emoji']
            disk_breakdown_header = f"{disk_breakdown_emoji} Disk Usage Breakdown:"
            message.append(f"{line_prefix}{disk_breakdown_header}{' ' * (content_width - len(disk_breakdown_header))}{line_suffix}")
            
            disk_breakdown = self.get_top_processes('Disk').split('\n')[:3]  # Limit to 3 entries
            for entry in disk_breakdown:
                message.append(f"{line_prefix}{entry}{' ' * (content_width - len(entry))}{line_suffix}")
        
        # Add bottom border
        message.append(self.config['alert_format_bottom_border'])
        
        return "\n".join(message)

    def send_telegram_alert(self, alert_type, usage_value):
        current_time = int(time.time())
        alert_interval = self.config['check_interval'] * 10  # Minimum time between alerts
        
        # Check if we should send an alert (rate limiting)
        alert_key = alert_type.lower()
        if alert_key not in self.last_alert_times:
            self.last_alert_times[alert_key] = 0
        
        time_since_last_alert = current_time - self.last_alert_times[alert_key]
        if time_since_last_alert < alert_interval:
            self.logger.debug(f"{alert_type} alert cheklandi (so'nggi xabardan {time_since_last_alert} soniya o'tdi)")
            return False
        
        # Format message according to configuration
        message = self.format_alert_message(alert_type, usage_value)
        
        # Log the message
        self.logger.info('-' * 40)
        self.logger.info(message)
        
        # Send to Telegram with retry
        max_retries = 3
        retry = 0
        success = False
        
        while retry < max_retries and not success:
            try:
                self.logger.debug(f"Telegramga xabar yuborilmoqda: {alert_type}")
                
                # Send message
                url = f"https://api.telegram.org/bot{self.config['bot_token']}/sendMessage"
                payload = {
                    'chat_id': self.config['chat_id'],
                    'text': message,
                    'parse_mode': 'HTML'
                }
                
                response = requests.post(url, json=payload, timeout=30)
                
                if response.status_code == 200 and response.json().get('ok'):
                    self.logger.info(f"{alert_type} alert xabari Telegramga muvaffaqiyatli yuborildi")
                    success = True
                    self.last_alert_times[alert_key] = current_time
                    
                    # Increment Prometheus counter if enabled
                    if self.config['prometheus_enabled']:
                        if alert_type == 'RAM':
                            self.prom_ram_alerts.inc()
                        elif alert_type == 'CPU':
                            self.prom_cpu_alerts.inc()
                        elif alert_type == 'Disk':
                            self.prom_disk_alerts.inc()
                        elif alert_type == 'Swap':
                            self.prom_swap_alerts.inc()
                        elif alert_type == 'Load':
                            self.prom_load_alerts.inc()
                        elif alert_type == 'Network':
                            self.prom_network_alerts.inc()
                    
                    # Store alert in database if enabled
                    if self.config['db_enabled']:
                        self._store_alert(alert_type, usage_value, message, True)
                    
                else:
                    retry += 1
                    error_description = response.json().get('description', 'Unknown error')
                    self.logger.warning(f"Telegramga xabar yuborishda xatolik (urinish {retry}/{max_retries}): {error_description}")
                    time.sleep(2)  # Wait before retrying
                    
            except Exception as e:
                retry += 1
                self.logger.warning(f"Telegramga xabar yuborishda xatolik (urinish {retry}/{max_retries}): {e}")
                time.sleep(2)  # Wait before retrying
        
        # If all retries failed
        if not success:
            self.logger.error(f"Telegramga xabar yuborib bo'lmadi ({max_retries} urinishdan so'ng)")
            self.logger.error(f"BOT_TOKEN: {self.config['bot_token'][:5]}...{self.config['bot_token'][-5:]}")
            self.logger.error(f"CHAT_ID: {self.config['chat_id']}")
            
            # Store failed alert in database if enabled
            if self.config['db_enabled']:
                self._store_alert(alert_type, usage_value, message, False)
            
            return False
        
        return True

    def test_telegram_connection(self):
        self.logger.info('Telegram bog\'lanishini tekshirish...')
        
        # Format test message according to configuration
        system_info = self.get_system_info()
        date_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if self.config['alert_format_enabled']:
            width = self.config['alert_format_width']
            line_prefix = self.config['alert_format_line_prefix']
            line_suffix = self.config['alert_format_line_suffix']
            content_width = width - len(line_prefix) - len(line_suffix)
            
            message = []
            message.append(self.config['alert_format_top_border'])
            message.append(f"{line_prefix}🔄 SYSTEM MONITOR TEST MESSAGE{' ' * (content_width - len('🔄 SYSTEM MONITOR TEST MESSAGE'))}{line_suffix}")
            message.append(self.config['alert_format_title_border'])
            message.append(f"{line_prefix}🖥️ Hostname:     {system_info['hostname']}{' ' * (content_width - len('🖥️ Hostname:     ') - len(system_info['hostname']))}{line_suffix}")
            message.append(f"{line_prefix}🌐 IP Address:   {system_info['ip']}{' ' * (content_width - len('🌐 IP Address:   ') - len(system_info['ip']))}{line_suffix}")
            message.append(f"{line_prefix}⏱️ Time:         {date_str}{' ' * (content_width - len('⏱️ Time:         ') - len(date_str))}{line_suffix}")
            message.append(self.config['alert_format_bottom_border'])
            message = "\n".join(message)
        else:
            message = "🔄 SYSTEM MONITOR TEST MESSAGE\n\n"
            message += f"🖥️ Hostname: {system_info['hostname']}\n"
            message += f"🌐 IP Address: {system_info['ip']}\n"
            message += f"⏱️ Time: {date_str}"
        
        try:
            url = f"https://api.telegram.org/bot{self.config['bot_token']}/sendMessage"
            payload = {
                'chat_id': self.config['chat_id'],
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200 and response.json().get('ok'):
                self.logger.info('Telegram bog\'lanishi muvaffaqiyatli tekshirildi')
                return True
            else:
                error_description = response.json().get('description', 'Unknown error')
                self.logger.error(f"Telegram bog'lanishini tekshirishda xatolik: {error_description}")
                self.logger.error(f"BOT_TOKEN: {self.config['bot_token'][:5]}...{self.config['bot_token'][-5:]}")
                self.logger.error(f"CHAT_ID: {self.config['chat_id']}")
                return False
                
        except Exception as e:
            self.logger.error(f"Telegram bog'lanishini tekshirishda xatolik: {e}")
            return False

    def _store_metrics(self, metrics, system_info):
        if not self.config['db_enabled']:
            return False
        
        try:
            # Extract network metrics
            network_rx, network_tx = 0.0, 0.0
            if 'network' in metrics and isinstance(metrics['network'], list) and len(metrics['network']) == 2:
                network_rx, network_tx = metrics['network']
            
            # Prepare extra data (anything not in standard columns)
            extra_data = {}
            for key, value in metrics.items():
                if key not in ['ram', 'cpu', 'disk', 'swap', 'load', 'network']:
                    extra_data[key] = value
            
            extra_data_json = json.dumps(extra_data) if extra_data else None
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            if self.config['db_type'] == 'sqlite':
                self.db_cursor.execute('''
                    INSERT INTO metrics (
                        timestamp, hostname, ip_address, ram_usage, cpu_usage, disk_usage, 
                        swap_usage, load_average, network_rx, network_tx, extra_data
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    timestamp,
                    system_info['hostname'],
                    system_info['ip'],
                    metrics.get('ram', 0.0),
                    metrics.get('cpu', 0.0),
                    metrics.get('disk', 0.0),
                    metrics.get('swap', 0.0),
                    metrics.get('load', 0.0),
                    network_rx,
                    network_tx,
                    extra_data_json
                ))
                
                self.db_conn.commit()
                
            elif self.config['db_type'] == 'mysql':
                self.db_cursor.execute('''
                    INSERT INTO metrics (
                        timestamp, hostname, ip_address, ram_usage, cpu_usage, disk_usage, 
                        swap_usage, load_average, network_rx, network_tx, extra_data
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (
                    timestamp,
                    system_info['hostname'],
                    system_info['ip'],
                    metrics.get('ram', 0.0),
                    metrics.get('cpu', 0.0),
                    metrics.get('disk', 0.0),
                    metrics.get('swap', 0.0),
                    metrics.get('load', 0.0),
                    network_rx,
                    network_tx,
                    extra_data_json
                ))
                
                self.db_conn.commit()
                
            elif self.config['db_type'] == 'postgresql':
                self.db_cursor.execute('''
                    INSERT INTO metrics (
                        timestamp, hostname, ip_address, ram_usage, cpu_usage, disk_usage, 
                        swap_usage, load_average, network_rx, network_tx, extra_data
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (
                    timestamp,
                    system_info['hostname'],
                    system_info['ip'],
                    metrics.get('ram', 0.0),
                    metrics.get('cpu', 0.0),
                    metrics.get('disk', 0.0),
                    metrics.get('swap', 0.0),
                    metrics.get('load', 0.0),
                    network_rx,
                    network_tx,
                    extra_data_json
                ))
                
                self.db_conn.commit()
            
            self.logger.debug("Metrics stored in database successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to store metrics in database: {e}")
            return False

    def _store_alert(self, alert_type, value, message, sent_successfully):
        if not self.config['db_enabled']:
            return False
        
        try:
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            system_info = self.get_system_info()
            
            if self.config['db_type'] == 'sqlite':
                self.db_cursor.execute('''
                    INSERT INTO alerts (
                        timestamp, hostname, alert_type, value, message, sent_successfully
                    ) VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    timestamp,
                    system_info['hostname'],
                    alert_type,
                    str(value),
                    message,
                    1 if sent_successfully else 0
                ))
                
                self.db_conn.commit()
                
            elif self.config['db_type'] == 'mysql':
                self.db_cursor.execute('''
                    INSERT INTO alerts (
                        timestamp, hostname, alert_type, value, message, sent_successfully
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                ''', (
                    timestamp,
                    system_info['hostname'],
                    alert_type,
                    str(value),
                    message,
                    sent_successfully
                ))
                
                self.db_conn.commit()
                
            elif self.config['db_type'] == 'postgresql':
                self.db_cursor.execute('''
                    INSERT INTO alerts (
                        timestamp, hostname, alert_type, value, message, sent_successfully
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                ''', (
                    timestamp,
                    system_info['hostname'],
                    alert_type,
                    str(value),
                    message,
                    sent_successfully
                ))
                
                self.db_conn.commit()
            
            self.logger.debug(f"Alert stored in database successfully: {alert_type}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to store alert in database: {e}")
            return False

    def update_prometheus_metrics(self, metrics):
        if not self.config['prometheus_enabled']:
            return False
        
        try:
            # Update resource usage gauges
            self.prom_ram_usage.set(metrics.get('ram', 0))
            self.prom_cpu_usage.set(metrics.get('cpu', 0))
            self.prom_disk_usage.set(metrics.get('disk', 0))
            self.prom_swap_usage.set(metrics.get('swap', 0))
            self.prom_load_average.set(metrics.get('load', 0))
            
            # Update network metrics
            if 'network' in metrics and isinstance(metrics['network'], list) and len(metrics['network']) == 2:
                self.prom_network_rx.set(metrics['network'][0])
                self.prom_network_tx.set(metrics['network'][1])
            
            self.logger.debug("Prometheus metrics updated successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update Prometheus metrics: {e}")
            return False

    def update_status_file(self, metrics):
        status_file = '/tmp/memory-monitor-status.tmp'
        date_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        try:
            status_content = f"So'nggi tekshirish: {date_str}\n"
            
            for key, value in metrics.items():
                if key == 'ram':
                    status_content += f"RAM: {value}%\n"
                elif key == 'cpu' and self.config['monitor_cpu']:
                    status_content += f"CPU: {value}%\n"
                elif key == 'disk' and self.config['monitor_disk']:
                    status_content += f"Disk ({self.config['disk_path']}): {value}%\n"
                elif key == 'swap' and self.config['monitor_swap'] and value > 0:
                    status_content += f"Swap: {value}%\n"
                elif key == 'load' and self.config['monitor_load']:
                    load_per_core = value / 100  # Convert back from percentage
                    load_1min = load_per_core * psutil.cpu_count(logical=True)
                    status_content += f"Load: {load_1min:.2f} (core boshiga: {load_per_core:.2f})\n"
                elif key == 'network' and self.config['monitor_network']:
                    rx_rate, tx_rate = value
                    status_content += f"Network ({self.config['network_interface']}): RX: {rx_rate:.2f} Mbps, TX: {tx_rate:.2f} Mbps\n"
            
            with open(status_file, 'w') as f:
                f.write(status_content)
                
        except Exception as e:
            self.logger.error(f"Status faylini yangilashda xatolik: {e}")

    def run(self):
        self.logger.info(f"Monitoring boshlandi. Interval: {self.config['check_interval']} soniya")
        
        while True:
            try:
                # Collect all metrics
                metrics = {
                    'ram': self.check_ram_usage(),
                    'cpu': self.check_cpu_usage(),
                    'disk': self.check_disk_usage(),
                    'swap': self.check_swap_usage(),
                    'load': self.check_load_average(),
                    'network': self.check_network_usage()
                }
                
                # Get system info for database and alerts
                system_info = self.get_system_info()
                
                # Store metrics in database if enabled
                if self.config['db_enabled']:
                    self._store_metrics(metrics, system_info)
                
                # Update Prometheus metrics if enabled
                if self.config['prometheus_enabled']:
                    self.update_prometheus_metrics(metrics)
                
                # Update status file
                self.update_status_file(metrics)
                
                # Check thresholds and send alerts
                
                # RAM check
                if metrics['ram'] >= self.config['threshold']:
                    self.logger.warning(f"Yuqori RAM ishlatilishi: {metrics['ram']}%")
                    self.send_telegram_alert('RAM', f"{metrics['ram']}%")
                
                # CPU check
                if self.config['monitor_cpu'] and metrics['cpu'] >= self.config['cpu_threshold']:
                    self.logger.warning(f"Yuqori CPU ishlatilishi: {metrics['cpu']}%")
                    self.send_telegram_alert('CPU', f"{metrics['cpu']}%")
                
                # Disk check
                if self.config['monitor_disk'] and metrics['disk'] >= self.config['disk_threshold']:
                    self.logger.warning(f"Yuqori disk ishlatilishi ({self.config['disk_path']}): {metrics['disk']}%")
                    self.send_telegram_alert('Disk', f"{metrics['disk']}%")
                
                # Swap check
                if self.config['monitor_swap'] and metrics['swap'] >= self.config['swap_threshold'] and metrics['swap'] > 0:
                    self.logger.warning(f"Yuqori swap ishlatilishi: {metrics['swap']}%")
                    self.send_telegram_alert('Swap', f"{metrics['swap']}%")
                
                # Load check
                if self.config['monitor_load'] and metrics['load'] >= self.config['load_threshold']:
                    load_per_core = metrics['load'] / 100  # Convert back from percentage
                    load_1min = load_per_core * psutil.cpu_count(logical=True)
                    self.logger.warning(f"Yuqori load average: {load_1min:.2f} (core boshiga: {load_per_core:.2f})")
                    self.send_telegram_alert('Load', f"{load_1min:.2f} (core boshiga: {load_per_core:.2f})")
                
                # Network check
                if self.config['monitor_network']:
                    rx_rate, tx_rate = metrics['network']
                    if rx_rate >= self.config['network_threshold'] or tx_rate >= self.config['network_threshold']:
                        self.logger.warning(f"Yuqori network trafigi ({self.config['network_interface']}): RX: {rx_rate:.2f} Mbps, TX: {tx_rate:.2f} Mbps")
                        self.send_telegram_alert('Network', f"RX: {rx_rate:.2f} Mbps, TX: {tx_rate:.2f} Mbps")
                
            except Exception as e:
                self.logger.error(f"Monitoring jarayonida xatolik: {e}")
            
            # Wait for next check
            time.sleep(self.config['check_interval'])

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='System Memory, CPU and Disk Monitoring')
    parser.add_argument('--config', default=DEFAULT_CONFIG_FILE, help=f'Configuration file path (default: {DEFAULT_CONFIG_FILE})')
    parser.add_argument('--version', action='store_true', help='Show version information')
    
    args = parser.parse_args()
    
    if args.version:
        print("System Monitor 1.2.0")
        sys.exit(0)
    
    monitor = SystemMonitor(args.config)
    monitor.run()

if __name__ == "__main__":
    main()
