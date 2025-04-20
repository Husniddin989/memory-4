# Memory Monitor

Tizim resurslarini kuzatish va Telegram orqali xabar yuborish uchun dastur.

## Asosiy xususiyatlar

- RAM foydalanishini kuzatish
- CPU foydalanishini kuzatish
- Disk foydalanishini kuzatish
- Swap foydalanishini kuzatish
- Tizim yuklamasini kuzatish
- Tarmoq trafikini kuzatish
- Telegram orqali xabarlar yuborish
- Dinamik alert formati
- Ma'lumotlar bazasi integratsiyasi (SQLite, MySQL, PostgreSQL)
- Prometheus/Grafana integratsiyasi

## O'rnatish

```bash
sudo ./install.sh
```

O'rnatish jarayonida qo'shimcha integratsiyalarni tanlashingiz mumkin:
- SQLite integratsiyasi
- MySQL integratsiyasi
- PostgreSQL integratsiyasi
- Prometheus integratsiyasi

## Konfiguratsiya

Konfiguratsiya fayli `/etc/memory-monitor/config.conf` manzilida joylashgan.

### Asosiy sozlamalar

```ini
[General]
bot_token = YOUR_TELEGRAM_BOT_TOKEN
chat_id = YOUR_TELEGRAM_CHAT_ID
log_file = /var/log/memory_monitor.log
log_level = INFO
threshold = 80
check_interval = 60
alert_message_title = 🖥️ SYSTEM STATUS ALERT
include_top_processes = true
top_processes_count = 10
```

### Alert format sozlamalari

Alert formatini sozlash uchun `[AlertFormat]` bo'limidan foydalaning. Batafsil ma'lumot uchun `FORMAT_GUIDE.md` faylini o'qing.

## Ishga tushirish

```bash
# Xizmatni yoqish
sudo systemctl enable memory-monitor.service

# Xizmatni ishga tushirish
sudo systemctl start memory-monitor.service

# Xizmat holatini tekshirish
sudo systemctl status memory-monitor.service
```

## Telegram xabar yuborishni tekshirish

```bash
sudo /opt/memory-monitor/test_telegram.py
```

## Log fayli

```bash
tail -f /var/log/memory_monitor.log
```

## Versiya

1.2.0
