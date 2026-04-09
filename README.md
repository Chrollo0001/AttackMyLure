# AttackMyLure – Python Honeypot

A lightweight, multi-service honeypot written in Python.  It simulates four
commonly targeted services (SSH, HTTP, FTP, Telnet), captures every
connection and authentication attempt, and writes structured (JSON-lines) logs
for later analysis.

---

## Features

| Service | Default port | What is logged |
|---------|-------------|----------------|
| SSH     | 2222        | IP, username, password / public-key type |
| HTTP    | 8080        | IP, GET paths, POST credentials |
| FTP     | 2121        | IP, username, password |
| Telnet  | 2323        | IP, username, password |

- **Realistic banners** – services identify themselves as common real software.
- **Structured logging** – every event is a JSON line in `logs/honeypot.log`.
- **Human-readable console output** – timestamped messages via Python `logging`.
- **Daemon threads** – all services run concurrently in a single process.
- **Easy to configure** – change ports, banners and log paths in `config.py`.

---

## Requirements

- Python 3.10+
- [paramiko](https://www.paramiko.org/) (for the SSH service)

```bash
pip install -r requirements.txt
```

---

## Quick start

```bash
# Clone and enter the repository
git clone https://github.com/Chrollo0001/AttackMyLure.git
cd AttackMyLure

# Install dependencies
pip install -r requirements.txt

# Start the honeypot
python honeypot.py
```

By default the honeypot binds to `0.0.0.0` on high ports (2222, 8080, 2121,
2323) so it can be run as a regular user.  Edit `config.py` to use the
standard ports 22 / 80 / 21 / 23 if running as root or with the required
capabilities.

---

## Log format

Each event is written as a single JSON object on its own line:

```json
{"timestamp": "2024-04-09T17:30:00.123456+00:00", "service": "SSH", "src_ip": "10.0.0.1", "src_port": 54321, "username": "admin", "password": "password123"}
{"timestamp": "2024-04-09T17:30:05.654321+00:00", "service": "HTTP", "src_ip": "10.0.0.2", "src_port": 61000, "username": "root", "password": "toor", "method": "POST", "path": "/login"}
```

---

## Project structure

```
AttackMyLure/
├── honeypot.py          # Entry-point – starts all services
├── config.py            # Ports, banners, log file path
├── logger.py            # Centralised JSON + console logging
├── requirements.txt
├── services/
│   ├── ssh_server.py    # Fake SSH service (paramiko)
│   ├── http_server.py   # Fake HTTP login page
│   ├── ftp_server.py    # Fake FTP service
│   └── telnet_server.py # Fake Telnet service
└── tests/
    └── test_honeypot.py # Unit + integration tests
```

---

## Running the tests

```bash
pip install -r requirements.txt
python -m pytest tests/ -v
```

---

## Legal notice

This tool is intended for use on systems you own or have explicit written
permission to test.  Deploying a honeypot on a network without authorisation
may be illegal in your jurisdiction.  Use responsibly.
