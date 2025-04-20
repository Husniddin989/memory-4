#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Telegram xabar yuborish testini tekshirish uchun skript
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
import psutil
from pathlib import Path

# Default configuration values
DEFAULT_CONFIG_FILE = '/home/ubuntu/memory-monitor-python-dynamic/config.conf'

class AlertTester:
    def __init__(self, config_file=DEFAULT_CONFIG_FILE):
        self.config_file = config_file
        self.config = self._load_config()
        
        print(f"Konfiguratsiya fayli: {self.config_file}")
        
    def _load_config(self):
        default_config = {
            'bot_token': "7120243579:AAEoaMz5DK8pv1uvwmbD--Mmt8nqbhL_mec",
            'chat_id': "664131109",
            'alert_message_title': "🖥️ SYSTEM STATUS ALERT",
            'include_top_processes': True,
            'top_processes_count': 10,
            # Alert format settings
            'alert_format_enabled': True,
            'alert_format_top_border': "┌────────────────────────────────────────────┐",
            'alert_format_title_border': "├────────────────────────────────────────────┤",
            'alert_format_section_border': "├────────────────────────────────────────────┤",
            'alert_format_bottom_border': "└────────────────────────────────────────────┘",
            'alert_format_line_prefix': "│ ",
            'alert_format_line_suffix': " │",
            'alert_format_date_emoji': "🗓️",
            'alert_format_ram_emoji': "🧠",
            'alert_format_cpu_emoji': "🔥",
            'alert_format_disk_emoji': "💾",
            'alert_format_top_processes_emoji': "🧾",
            'alert_format_disk_breakdown_emoji': "📁",
            'alert_format_hostname_emoji': "",
            'alert_format_ip_emoji': "",
            'alert_format_uptime_emoji': "",
            'alert_format_os_emoji': "",
            'alert_format_kernel_emoji': "",
            'alert_format_use_box_drawing': True,
            'alert_format_width': 44,
            'alert_format_title_align': "center",  # left, center, right
            'alert_format_include_system_info': True,
            'alert_format_include_resources': True,
            'alert_format_include_top_processes': True,
            'alert_format_include_disk_breakdown': True
        }

        try:
            if not os.path.exists(self.config_file):
                print(f"XATO: Konfiguratsiya fayli topilmadi: {self.config_file}")
                print("Standart konfiguratsiya qiymatlari ishlatiladi.")
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
                if 'alert_message_title' in config['General']:
                    result['alert_message_title'] = config['General']['alert_message_title']
                
                if 'top_processes_count' in config['General']:
                    result['top_processes_count'] = int(config['General']['top_processes_count'])
                
                if 'include_top_processes' in config['General']:
                    result['include_top_processes'] = config['General'].getboolean('include_top_processes')
            
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
            
            return result
            
        except Exception as e:
            print(f"Konfiguratsiya faylini o'qishda xatolik: {e}")
            print("Standart konfiguratsiya qiymatlari ishlatiladi.")
            return default_config

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
        
        # Get OS info
        os_info = f"{platform.system()} {platform.release()}"
        try:
            import subprocess
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
        
        # Get memory info
        mem = psutil.virtual_memory()
        total_memory_gb = mem.total / (1024 ** 3)
        ram_usage = mem.percent
        
        # Get CPU info
        cpu_usage = psutil.cpu_percent(interval=1)
        
        # Get disk info
        disk_usage = psutil.disk_usage('/')
        total_disk_gb = disk_usage.total / (1024 ** 3)
        disk_percent = disk_usage.percent
        
        return {
            'hostname': hostname,
            'ip': server_ip,
            'os': os_info,
            'kernel': platform.release(),
            'uptime': uptime,
            'ram_usage': ram_usage,
            'total_ram': f"{total_memory_gb:.1f}Gi",
            'cpu_usage': cpu_usage,
            'disk_usage': disk_percent,
            'total_disk': f"{total_disk_gb:.1f}G"
        }

    def get_top_processes(self, resource_type, count=3):
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
            
            elif resource_type == 'Disk':
                try:
                    import subprocess
                    output = subprocess.check_output(f"du -h /* 2>/dev/null | sort -rh | head -n {count}", shell=True).decode()
                    lines = output.strip().split('\n')
                    result = []
                    for line in lines:
                        if line:
                            parts = line.split('\t')
                            if len(parts) == 2:
                                size, path = parts
                                path = path.split('/')[-1]
                                result.append(f"  - /{path.ljust(15)} {size}")
                    return "\n".join(result)
                except:
                    return "Could not get disk usage information"
            
            return "Unknown resource type"
        except Exception as e:
            return f"Error getting top processes: {e}"

    def format_alert_message(self):
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
            ram_usage = system_info['ram_usage']
            cpu_usage = system_info['cpu_usage']
            disk_usage = system_info['disk_usage']
            
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
        ram_usage = system_info['ram_usage']
        cpu_usage = system_info['cpu_usage']
        disk_usage = system_info['disk_usage']
        
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

    def send_telegram_message(self):
        # Format message according to configuration
        message = self.format_alert_message()
        
        # Log the message
        print('-' * 40)
        print(message)
        
        # Send to Telegram with retry
        max_retries = 3
        retry = 0
        success = False
        
        while retry < max_retries and not success:
            try:
                print(f"Telegramga xabar yuborilmoqda...")
                
                # Send message
                url = f"https://api.telegram.org/bot{self.config['bot_token']}/sendMessage"
                payload = {
                    'chat_id': self.config['chat_id'],
                    'text': message,
                    'parse_mode': 'HTML'
                }
                
                response = requests.post(url, json=payload, timeout=30)
                
                if response.status_code == 200 and response.json().get('ok'):
                    print(f"✅ Xabar muvaffaqiyatli yuborildi!")
                    success = True
                else:
                    retry += 1
                    error_description = response.json().get('description', 'Unknown error')
                    print(f"❌ Telegramga xabar yuborishda xatolik (urinish {retry}/{max_retries}): {error_description}")
                    print(f"Status code: {response.status_code}")
                    print(f"Response: {response.text}")
                    time.sleep(2)  # Wait before retrying
                    
            except Exception as e:
                retry += 1
                print(f"❌ Telegramga xabar yuborishda xatolik (urinish {retry}/{max_retries}): {e}")
                time.sleep(2)  # Wait before retrying
        
        # If all retries failed
        if not success:
            print(f"❌ Telegramga xabar yuborib bo'lmadi ({max_retries} urinishdan so'ng)")
            print(f"BOT_TOKEN: {self.config['bot_token'][:5]}...{self.config['bot_token'][-5:]}")
            print(f"CHAT_ID: {self.config['chat_id']}")
            return False
        
        return True

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Test Telegram Alert Formatting')
    parser.add_argument('--config', default=DEFAULT_CONFIG_FILE, help=f'Configuration file path (default: {DEFAULT_CONFIG_FILE})')
    
    args = parser.parse_args()
    
    print("Telegram xabar yuborish testini boshlash...")
    tester = AlertTester(args.config)
    result = tester.send_telegram_message()
    
    if result:
        print("Test muvaffaqiyatli yakunlandi!")
    else:
        print("Test muvaffaqiyatsiz yakunlandi!")

if __name__ == "__main__":
    main()
