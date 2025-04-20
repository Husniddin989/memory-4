# Python Monitoring Skriptini Ma'lumotlar Bazasi va Prometheus bilan Integratsiya Qilish Bo'yicha Qo'llanma

Bu qo'llanma Python versiyasidagi monitoring skriptini ma'lumotlar bazasi va Prometheus bilan integratsiya qilish uchun batafsil ko'rsatmalarni o'z ichiga oladi.

## 1. Ma'lumotlar Bazasi Integratsiyasi

### 1.1. SQLite bilan Integratsiya

SQLite eng oddiy ma'lumotlar bazasi bo'lib, alohida server talab qilmaydi va bitta faylda saqlaydi. Bitta server uchun yaxshi tanlov.

#### Kerakli Paketlarni O'rnatish

```bash
pip install sqlite3
```

#### Konfiguratsiya Faylini Sozlash

`config.conf` faylida quyidagi sozlamalarni yoqing:

```ini
[Database]
db_enabled = true
db_type = sqlite
db_path = /var/lib/memory-monitor/metrics.db
```

#### SQLite Ma'lumotlar Bazasini Yaratish

SQLite ma'lumotlar bazasi avtomatik ravishda yaratiladi, lekin katalogni oldindan yaratish kerak:

```bash
sudo mkdir -p /var/lib/memory-monitor
sudo chmod 755 /var/lib/memory-monitor
```

### 1.2. MySQL bilan Integratsiya

MySQL bir nechta serverlarni markazlashtirilgan kuzatish uchun yaxshi tanlov.

#### Kerakli Paketlarni O'rnatish

```bash
pip install mysql-connector-python
```

#### MySQL Serverini O'rnatish (agar o'rnatilmagan bo'lsa)

```bash
sudo apt update
sudo apt install mysql-server
```

#### MySQL Ma'lumotlar Bazasini Yaratish

```bash
sudo mysql -e "CREATE DATABASE system_monitor;"
sudo mysql -e "CREATE USER 'monitor'@'localhost' IDENTIFIED BY 'password';"
sudo mysql -e "GRANT ALL PRIVILEGES ON system_monitor.* TO 'monitor'@'localhost';"
sudo mysql -e "FLUSH PRIVILEGES;"
```

#### Konfiguratsiya Faylini Sozlash

`config.conf` faylida quyidagi sozlamalarni yoqing:

```ini
[Database]
db_enabled = true
db_type = mysql
db_host = localhost
db_port = 3306
db_name = system_monitor
db_user = monitor
db_password = password
```

### 1.3. PostgreSQL bilan Integratsiya

PostgreSQL katta ma'lumotlar to'plamlari uchun yaxshi ishlaydi.

#### Kerakli Paketlarni O'rnatish

```bash
pip install psycopg2-binary
```

#### PostgreSQL Serverini O'rnatish (agar o'rnatilmagan bo'lsa)

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

#### PostgreSQL Ma'lumotlar Bazasini Yaratish

```bash
sudo -u postgres psql -c "CREATE DATABASE system_monitor;"
sudo -u postgres psql -c "CREATE USER monitor WITH ENCRYPTED PASSWORD 'password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE system_monitor TO monitor;"
```

#### Konfiguratsiya Faylini Sozlash

`config.conf` faylida quyidagi sozlamalarni yoqing:

```ini
[Database]
db_enabled = true
db_type = postgresql
db_host = localhost
db_port = 5432
db_name = system_monitor
db_user = monitor
db_password = password
```

### 1.4. Ma'lumotlar Bazasidan Foydalanish

Ma'lumotlar bazasiga saqlangan ma'lumotlarni ko'rish uchun:

#### SQLite

```bash
sqlite3 /var/lib/memory-monitor/metrics.db "SELECT * FROM metrics ORDER BY timestamp DESC LIMIT 10;"
```

#### MySQL

```bash
mysql -u monitor -p -e "USE system_monitor; SELECT * FROM metrics ORDER BY timestamp DESC LIMIT 10;"
```

#### PostgreSQL

```bash
psql -U monitor -d system_monitor -c "SELECT * FROM metrics ORDER BY timestamp DESC LIMIT 10;"
```

## 2. Prometheus Integratsiya

### 2.1. Prometheus Serverini O'rnatish

#### Prometheus O'rnatish

```bash
wget https://github.com/prometheus/prometheus/releases/download/v2.37.0/prometheus-2.37.0.linux-amd64.tar.gz
tar xvfz prometheus-2.37.0.linux-amd64.tar.gz
cd prometheus-2.37.0.linux-amd64/
```

#### Prometheus Konfiguratsiyasi

`prometheus.yml` faylini yarating:

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'system_monitor'
    static_configs:
      - targets: ['localhost:9090']
```

#### Prometheus Serverini Ishga Tushirish

```bash
./prometheus --config.file=prometheus.yml
```

### 2.2. Monitoring Skriptini Prometheus bilan Integratsiya Qilish

#### Kerakli Paketlarni O'rnatish

```bash
pip install prometheus_client
```

#### Konfiguratsiya Faylini Sozlash

`config.conf` faylida quyidagi sozlamalarni yoqing:

```ini
[Prometheus]
prometheus_enabled = true
prometheus_port = 9090
```

### 2.3. Prometheus Metrikalarini Tekshirish

Prometheus serverini ishga tushirgandan so'ng, brauzerda quyidagi URL orqali metrikalarni ko'rishingiz mumkin:

```
http://localhost:9090/graph
```

Quyidagi metrikalarni qidirishingiz mumkin:

- `system_monitor_ram_usage_percent`
- `system_monitor_cpu_usage_percent`
- `system_monitor_disk_usage_percent`
- `system_monitor_swap_usage_percent`
- `system_monitor_load_average`
- `system_monitor_network_rx_mbps`
- `system_monitor_network_tx_mbps`

## 3. Grafana bilan Integratsiya

### 3.1. Grafana O'rnatish

```bash
sudo apt-get install -y apt-transport-https software-properties-common
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
echo "deb https://packages.grafana.com/oss/deb stable main" | sudo tee -a /etc/apt/sources.list.d/grafana.list
sudo apt-get update
sudo apt-get install grafana
sudo systemctl start grafana-server
sudo systemctl enable grafana-server
```

### 3.2. Grafana Konfiguratsiyasi

1. Brauzerda Grafana veb-interfeysini oching (standart: http://localhost:3000)
2. Standart login ma'lumotlari bilan kiring (admin/admin)
3. Konfiguratsiya > Ma'lumotlar manbalari bo'limiga o'ting
4. "Ma'lumotlar manbai qo'shish" tugmasini bosing
5. "Prometheus" ni tanlang
6. URL maydoniga Prometheus serveri manzilini kiriting (masalan, http://localhost:9090)
7. "Saqlash va Sinov" tugmasini bosing

### 3.3. Grafana Dashboard Yaratish

1. "+" belgisini bosing va "Import" ni tanlang
2. Monitoring skripti bilan birga kelgan dashboard JSON faylini yuklang
3. Prometheus ma'lumotlar manbasini tanlang
4. "Import" tugmasini bosing

## 4. Xatolarni Bartaraf Etish

### 4.1. Ma'lumotlar Bazasi Xatolari

#### SQLite Xatolari

```
Error: unable to open database file
```

Yechim: Ma'lumotlar bazasi katalogini yarating va ruxsatlarni tekshiring:

```bash
sudo mkdir -p /var/lib/memory-monitor
sudo chmod 755 /var/lib/memory-monitor
sudo chown $USER:$USER /var/lib/memory-monitor
```

#### MySQL Xatolari

```
Error: Access denied for user 'monitor'@'localhost'
```

Yechim: Foydalanuvchi va ruxsatlarni tekshiring:

```bash
sudo mysql -e "GRANT ALL PRIVILEGES ON system_monitor.* TO 'monitor'@'localhost';"
sudo mysql -e "FLUSH PRIVILEGES;"
```

#### PostgreSQL Xatolari

```
Error: FATAL: password authentication failed for user "monitor"
```

Yechim: Foydalanuvchi va parolni tekshiring:

```bash
sudo -u postgres psql -c "ALTER USER monitor WITH PASSWORD 'password';"
```

### 4.2. Prometheus Xatolari

```
Error: Failed to listen on :9090: listen tcp 0.0.0.0:9090: bind: address already in use
```

Yechim: Boshqa port tanlang:

```ini
[Prometheus]
prometheus_enabled = true
prometheus_port = 9091
```

### 4.3. Grafana Xatolari

```
Error: Data source connection failed
```

Yechim: Prometheus serverining ishlab turganligini va URL to'g'ri ekanligini tekshiring:

```bash
curl http://localhost:9090/api/v1/status/config
```

## 5. Xavfsizlik Maslahatlar

1. **Ma'lumotlar bazasi parollari**: Kuchli parollardan foydalaning va ularni xavfsiz saqlang
2. **Ma'lumotlar bazasi foydalanuvchilari**: Minimal ruxsatlar bilan foydalanuvchilar yarating
3. **Prometheus endpointi**: Agar ommaviy tarmoqda ochilsa, autentifikatsiya qo'shing
4. **Log fayllari**: Log fayllarida maxfiy ma'lumotlar yo'qligini tekshiring
5. **Root sifatida ishga tushirish**: Imkon qadar, xizmatni minimal ruxsatlar bilan noroot foydalanuvchi sifatida ishga tushiring

## 6. Ishlash Samaradorligi Maslahatlar

1. **Tekshirish oralig'i**: Tekshirish oralig'ini serveringiz quvvatiga qarab sozlang
2. **Ma'lumotlar bazasi saqlash**: Uzoq muddatli saqlash uchun ma'lumotlar bazasi indekslash va partitsiyalashni o'ylab ko'ring
3. **Top jarayonlar**: Top jarayonlarni yig'ish resurs talab qilishi mumkin; kerak bo'lmasa o'chirib qo'ying
4. **Prometheus metrikalar**: Yuqori chastotali so'rovlar ishlashga ta'sir qilishi mumkin

## 7. Qo'shimcha Resurslar

- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [MySQL Documentation](https://dev.mysql.com/doc/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
