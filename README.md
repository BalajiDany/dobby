# 🪄 Dobby: The Ultimate n8n Setup with Encrypted Git Backups

Stop worrying about losing your automation workflows. **Dobby** is a hardened, production-ready n8n deployment kit
designed specifically for Raspberry Pi and home servers. It doesn't just run n8n; it protects it.

## ✨ Why Dobby?

Most n8n setups are fragile. If your SD card fails or your Docker volume gets corrupted, your workflows are gone. Dobby
changes that:

* **⚡ Optimized for Performance:** Built with Python 3.12 and `uv` for a tiny footprint—perfect for Raspberry Pi.
* **🔒 Military-Grade Security:** Every backup is compressed with `zlib` and encrypted with **AES-256 (Fernet)** before
  it ever leaves your server.
* **automated Git Sync:** Automatically pushes your encrypted database dumps to a private GitHub repository every night
  at 1:00 AM.
* **🛠️ One-Click Restore:** A built-in FastAPI management layer allows you to restore your entire instance from a
  specific date via a simple API call.
* **🚀 Scalable Architecture:** Includes **n8n-runners** by default to handle heavy workloads without slowing down the
  UI.

---

## 🏗️ Core Architecture

Dobby runs as a multi-container orchestration:

1. **n8n:** The automation engine.
2. **Postgres 18:** The modern, high-performance database.
3. **n8n-runners:** Dedicated workers for task execution.
4. **Dobby Core:** The "brain" that handles scheduling, encryption, and GitHub synchronization.

---

## 🚀 Quick Start

### 1. Clone & Configure

```bash
git clone https://github.com/your-username/n8n-dobby.git
cd n8n-dobby
cp .env.template .env

```

### 2. Fill in your `.env`

You'll need a GitHub Personal Access Token (PAT) with `repo` scope and a Fernet encryption key.

### 3. Deploy

```bash
docker-compose up -d --build

```

Your n8n instance is now live at `http://<your-ip>:5678` and your management API is at `http://<your-ip>:8000`.

---

## 🛠️ Management API

Dobby provides a lightweight API to manage your instance state:

| Endpoint                | Method | Description                                             |
|-------------------------|--------|---------------------------------------------------------|
| `/health`               | `GET`  | Check if the backup engine is running.                  |
| `/backup`               | `GET`  | Trigger an immediate manual encrypted backup to GitHub. |
| `/restore/{YYYY-MM-DD}` | `GET`  | Pull, decrypt, and restore the DB from a specific date. |

---

## 🛡️ Security First

Your data is never stored in plain text on GitHub. Even if your backup repository is compromised, your workflows remain
safe behind your `BACKUP_ENCRYPTION_KEY`.

**Keep this key safe; without it, your backups are undecipherable.**

---

## 📈 Perfect for Raspberry Pi

Dobby was born on a Raspberry Pi 4/5. By offloading task execution to the `n8n-runners` and using the debian-slim Python
builds, we ensure maximum uptime and minimum thermal throttling.
