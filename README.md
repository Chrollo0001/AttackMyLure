# 🍯 AttackMyLure - Multi-Protocol Honeypot

A high-interaction honeypot designed to detect and log network attacks across multiple protocols (SSH, HTTP). Capture malicious commands, payloads, and gather geolocation intelligence in real-time.

---

## 📊 Features

- **Multi-Protocol Luring**
  - 🔐 SSH Server (Port 2222) - Full shell emulation with command logging
  - 🌐 HTTP Lure (Port 80) - Fake admin panel
  
- **Advanced Logging**
  - 📍 GeoIP Detection (Country, City, ISP)
  - 🎯 Payload Capture (Auto-download malicious scripts from curl/wget commands)
  - ⏱️ Real-time Attack Timeline
  - 💾 MySQL Database Storage

- **Interactive Dashboard**
  - 📈 Top 10 Commands Chart
  - 🔀 Protocol Distribution
  - 📍 Top Cities Attack Map
  - ⚡ Real-time Attack Alerts (5 latest attacks)
  - 📦 Captured Payloads Library
  - ⏰ 24H Attack Timeline

---

## 📋 Data Collected

```
- Timestamp
- Protocol (SSH, HTTP, COMMAND)
- IP Address
- Country, City, ISP
- Username & Password (attempts)
- Command Executed
- Client Version
- Payload Files (if curl/wget detected)
```

---

## 🚀 Installation & Quick Start

### Prerequisites
- **Python 3.8+**
- **MySQL/MariaDB** (XAMPP recommended for Windows)
- **PHP 7.4+** (for dashboard)
- Windows or Linux

### Step 1: Clone & Setup Python Backend
```bash
git clone https://github.com/Chrollo0001/AttackMyLure.git
cd AttackMyLure
pip install -r requirements.txt
```

### Step 2: Configure Database
1. **Create MySQL Database:**
   ```sql
   CREATE DATABASE attack_my_lure;
   ```

2. **Create Attacks Table:**
   ```sql
   CREATE TABLE attacks (
       id INT AUTO_INCREMENT PRIMARY KEY,
       timestamp DATETIME,
       protocol VARCHAR(50),
       ip_address VARCHAR(45),
       country VARCHAR(100),
       city VARCHAR(100),
       isp VARCHAR(100),
       username VARCHAR(255),
       password VARCHAR(255),
       command TEXT,
       client_version VARCHAR(100)
   );
   ```

3. **Configure Credentials** in `src/logger.py`:
   ```python
   self.config = {
       'user': 'root',
       'password': 'your_password',
       'host': '127.0.0.1',
       'database': 'attack_my_lure'
   }
   ```

### Step 3: Setup Dashboard (XAMPP on Windows)
1. Copy the `dashboard/` folder to `C:\xampp\htdocs\dashboard`
2. Update `dashboard/api.php` with your database credentials
3. Ensure MySQL is running in XAMPP

### Step 4: Run the Honeypot
```bash
python src/main.py
```

You should see:
```
[*] Loading SSH KEY
[*] AttackMyLure est en ligne sur le port 2222
[*] HTTP Lure est en ligne sur le port 80
[*] Système Multi-Leurre activé. Bonne chasse !
```

### Step 5: Access Dashboard
- Open browser → `http://localhost/dashboard/index.php`
- See real-time attacks, commands, and captured payloads

---

## 🎯 Usage

### Test SSH Connection
```bash
ssh -p 2222 anyuser@127.0.0.1
# Password: anything (it logs the attempt)
```

### Test Payload Capture
Once connected via SSH:
```bash
curl http://example.com
wget https://raw.githubusercontent.com/some/script.sh
```
Files are automatically captured to `src/captured_payloads/`

### Test HTTP Lure
```bash
curl http://localhost/
```

---

## 📁 Project Structure

```
AttackMyLure/
├── src/
│   ├── main.py                 # Main honeypot server
│   ├── ssh_module.py           # SSH server & payload capture
│   ├── logger.py               # Database logging
│   ├── captured_payloads/      # Downloaded malicious files
│   └── private_key.key         # SSH host key (auto-generated)
├── dashboard/
│   ├── index.php               # Web dashboard UI
│   └── api.php                 # JSON API for data
├── requirements.txt            # Python dependencies
└── README.md
```

---

## 🔧 Configuration

### Change SSH Port
Edit `src/main.py`:
```python
server_socket.bind(('0.0.0.0', 2222))  # Change 2222 to your port
```

### Change HTTP Port
```python
server_socket.bind(('0.0.0.0', 80))  # Change 80 to your port
```

### Customize Fake HTTP Response
Edit `src/main.py` in `http_lure()` function

---

## 📊 Dashboard Features

- **TOP_10_COMMANDS**: Most executed commands
- **PROTOCOL_DISTRIBUTION**: SSH vs HTTP attacks
- **TOP_CITIES**: Geographic heatmap of attacks
- **ATTACK_TIMELINE_24H**: Hourly attack frequency
- **REAL_TIME_ALERTS**: Last 5 attacks (refreshes every 5 seconds)
- **CAPTURED_PAYLOADS_DB**: Downloaded malicious scripts

---

## 🔐 Security Notes

⚠️ **Warning**: This is a honeypot for research/education only!
- Run on isolated networks or VMs
- Never expose directly to untrusted networks without proper isolation
- Monitor for actual attacks using the dashboard
- Backup your `attack_my_lure` database regularly

---

## 🐛 Troubleshooting

### "Connection refused on port 2222"
- Run as admin (requires port 2222)
- Or change to port 22222+ (non-privileged)

### "Payloads not appearing in dashboard"
- Ensure `src/captured_payloads/` directory exists
- Check file permissions
- Verify dashboard API path in `api.php`

### "Database connection error"
- Ensure MySQL is running
- Check credentials in `src/logger.py`
- Verify database and table exist

---

## 📝 Contributing

Found a bug or have ideas? Feel free to:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

---

## 📄 License

This project is for educational and authorized security testing purposes only.

---

**Created by**: Chrollo0001  
**Last Updated**: 2026-04-11
