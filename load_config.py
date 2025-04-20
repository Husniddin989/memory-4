  
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
