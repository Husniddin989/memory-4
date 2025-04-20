# Dinamik Alert Formati Qo'llanmasi

Bu qo'llanma Memory Monitor dasturining alert formatini sozlash uchun ko'rsatmalarni o'z ichiga oladi.

## Alert Formati Sozlamalari

Alert formatini sozlash uchun konfiguratsiya faylidagi `[AlertFormat]` bo'limidan foydalaniladi. Quyida barcha mavjud sozlamalar keltirilgan:

### Asosiy Sozlamalar

```ini
[AlertFormat]
alert_format_enabled = true
```

`alert_format_enabled = false` qilib qo'yilsa, oddiy matn formatida xabarlar yuboriladi.

### Ramka Sozlamalari

```ini
alert_format_top_border = ┌────────────────────────────────────────────┐
alert_format_title_border = ├────────────────────────────────────────────┤
alert_format_section_border = ├────────────────────────────────────────────┤
alert_format_bottom_border = └────────────────────────────────────────────┘
alert_format_line_prefix = │ 
alert_format_line_suffix =  │
```

Bu sozlamalar xabar ramkasining ko'rinishini belgilaydi. Siz ularni o'zingizga mos ravishda o'zgartirishingiz mumkin.

### Kenglik va Joylashuv

```ini
alert_format_width = 44
alert_format_title_align = center
```

`alert_format_width` - xabar kengligi (belgilar soni)
`alert_format_title_align` - sarlavha joylashuvi (`left`, `center` yoki `right`)

### Emoji Belgilari

```ini
alert_format_date_emoji = 🗓️
alert_format_ram_emoji = 🧠
alert_format_cpu_emoji = 🔥
alert_format_disk_emoji = 💾
alert_format_top_processes_emoji = 🧾
alert_format_disk_breakdown_emoji = 📁
alert_format_hostname_emoji = 
alert_format_ip_emoji = 
alert_format_uptime_emoji = 
alert_format_os_emoji = 
alert_format_kernel_emoji = 
```

Har bir qator uchun emoji belgilarini o'zgartirishingiz yoki bo'sh qoldirishingiz mumkin.

### Bo'limlarni Yoqish/O'chirish

```ini
alert_format_include_system_info = true
alert_format_include_resources = true
alert_format_include_top_processes = true
alert_format_include_disk_breakdown = true
```

Bu sozlamalar orqali xabarda qaysi bo'limlar ko'rsatilishini boshqarishingiz mumkin.

## Misol Formatlar

### Standart Format

```
┌────────────────────────────────────────────┐
│          🖥️ SYSTEM STATUS ALERT          │
├────────────────────────────────────────────┤
│🗓️ Date:       2025-04-19 18:54:11        │
│ Hostname:     server1                     │
│ IP Address:   192.168.1.100              │
│ Uptime:       2h 12m                     │
│ OS:           Ubuntu 22.04.5 LTS         │
│ Kernel:       6.1.102                    │
├────────────────────────────────────────────┤
│🧠 RAM Usage:       24.5% of 3.8Gi         │
│🔥 CPU Usage:       1.3%                   │
│💾 Disk Usage:      36.8% of 12.2G         │
├────────────────────────────────────────────┤
│🧾 Top RAM Consumers:                      │
│  - chrome          (6.4%)                │
│  - python          (4.1%)                │
│  - chrome          (3.6%)                │
├────────────────────────────────────────────┤
│📁 Disk Usage Breakdown:                   │
│  - /usr             2.4G                 │
│  - /lib             1.2G                 │
│  - /opt             969M                 │
└────────────────────────────────────────────┘
```

### Oddiy Ramka

```ini
alert_format_top_border = +------------------------------------------+
alert_format_title_border = +------------------------------------------+
alert_format_section_border = +------------------------------------------+
alert_format_bottom_border = +------------------------------------------+
alert_format_line_prefix = | 
alert_format_line_suffix =  |
```

### Emoji Belgilarsiz

Barcha emoji sozlamalarini bo'sh qoldiring:

```ini
alert_format_date_emoji = 
alert_format_ram_emoji = 
alert_format_cpu_emoji = 
alert_format_disk_emoji = 
alert_format_top_processes_emoji = 
alert_format_disk_breakdown_emoji = 
```

### Faqat Resurslar

```ini
alert_format_include_system_info = false
alert_format_include_resources = true
alert_format_include_top_processes = false
alert_format_include_disk_breakdown = false
```

## Sozlamalarni Qo'llash

Konfiguratsiya faylini tahrirlash:

```bash
sudo nano /etc/memory-monitor/config.conf
```

O'zgarishlarni qo'llash uchun xizmatni qayta ishga tushiring:

```bash
sudo systemctl restart memory-monitor.service
```

Yangi formatni tekshirish:

```bash
sudo /opt/memory-monitor/test_telegram.py
```
