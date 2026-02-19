# VPS & Docker Monitor Bot

This project is a Telegram bot that allows you to **monitor a VPS and its Docker containers** automatically, sending real-time alerts and daily summaries. It is designed to run inside a Docker container and is securely deployed through **CI/CD with GitHub Actions**, ensuring that every update pushed to the repository is automatically reflected on your VPS.

## Project Goals

1. **VPS Resource Monitoring**

   * Real-time CPU, RAM, Disk, and Load Average metrics.
   * Automatic detection of resource usage spikes with alerts.

2. **Docker Container Monitoring**

   * Status of each container (`running` / stopped).
   * Alerts if any container goes down.

3. **Smart Alert System**

   * No spam: each alert remains active until the condition is resolved.
   * Alert types:

     * CPU > 80%
     * RAM > 85%
     * Disk > 85%
     * Container down

4. **Automatic Daily Summary**

   * A summary of VPS status, containers, and alerts from the last 24 hours is sent at 10:00 AM.

5. **Telegram Commands**

   * `/serverstatus` → VPS status and active alerts.
   * `/dockerstatus` → Docker container status.
   * `/alerts` → Current active alerts.

6. **Secure and Automated Deployment with CI/CD**

   * Every push to the `main` branch rebuilds and restarts the bot on the VPS.
   * Sensitive variables (BOT_TOKEN and CHAT_ID) are managed through GitHub Secrets and are not stored in the repository.

## Project Structure

```markdown
bot/
├── bot.py                # Main bot, commands, and daily summary
├── monitor.py            # VPS and container metrics collection
├── alerts.py             # Alert engine and state management
├── alert_engine.py       # Periodic alert checks and Telegram notifications
├── Dockerfile            # Container image
├── docker-compose.yml    # Container configuration and variables
├── requirements.txt      # Python dependencies
└── .github/
    └── workflows/
        └── deploy.yml    # GitHub Actions CI/CD
```

## Requirements

1. VPS with Docker and Docker Compose installed.
2. Telegram bot created with @BotFather.
3. GitHub repository with the code and configured GitHub Secrets.
4. SSH connection between GitHub Actions and your VPS.

## Configuring Secrets in GitHub

To keep sensitive variables out of the repository, you must use **GitHub Secrets**:

1. Go to **Settings → Secrets and variables → Actions → New repository secret**.
2. Create the following secrets:

| Name          | Value                                          |
| ------------- | ---------------------------------------------- |
| `VPS_HOST`    | VPS IP address or domain                       |
| `VPS_USER`    | SSH user to connect to the VPS                 |
| `VPS_SSH_KEY` | Private SSH key to access the VPS              |
| `VPS_SSH_PORT`| SSH por to connect to the VPS                  |
| `BOT_TOKEN`   | Your Telegram bot token (@BotFather)           |
| `CHAT_ID`     | Telegram chat ID where alerts will be received |

> These variables must never be committed to the repository.
> They are automatically injected during deployment on the VPS and into the Docker container.

---

## Docker Compose

`docker-compose.yml` file:

```yaml
services:
  bot-monitor:
    build: .
    container_name: bot-monitor
    restart: unless-stopped
    environment:
      BOT_TOKEN: ${BOT_TOKEN}
      CHAT_ID: ${CHAT_ID}
      TZ: Europe/Madrid
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - /etc/localtime:/etc/localtime:ro
      - /etc/timezone:/etc/timezone:ro
```

* The `/var/run/docker.sock` volume allows the bot to access and inspect Docker containers on the VPS.
* Environment variables are loaded from GitHub Secrets during deployment.

## CI/CD with GitHub Actions

Every push to the `main` branch triggers a workflow that:

1. Connects to the VPS via SSH using the private key stored in GitHub Secrets.
2. Navigates to the project directory on the VPS and runs `git pull` to update the code.
3. Rebuilds the Docker container (`docker compose build`).
4. Starts the updated container (`docker compose up -d`).

Example workflow (`.github/workflows/deploy.yml`):

```yaml
name: Deploy to VPS

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Deploy to VPS via SSH
        uses: appleboy/ssh-action@v1.0.3
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USER }}
          key: ${{ secrets.VPS_SSH_KEY }}
          port: ${{ secrets.VPS_SSH_PORT }}
          script: |
            cd /opt/bot-monitor
            git pull origin main
            export BOT_TOKEN=${{ secrets.BOT_TOKEN }}
            export CHAT_ID=${{ secrets.CHAT_ID }}
            docker compose down
            docker compose up -d --build
```

> `/opt/bot-monitor` is the directory where the project is located on the VPS.

## Bot Commands

| Command         | Function                     |
| --------------- | ---------------------------- |
| `/serverstatus` | VPS status and active alerts |
| `/dockerstatus` | Docker container status      |
| `/alerts`       | Current active alerts        |

## Expected Results

* Automatic alerts when:

  * CPU > 80%
  * RAM > 85%
  * Disk > 85%

* Notification when an alert condition is resolved
* Daily summary at 10:00 AM
* Quick access via `/serverstatus`, `/dockerstatus`, and `/alerts`
* CI/CD automatically deploying every update to the VPS

## Best Practices

* Monitor container logs:

```bash
docker logs -f bot-monitor
```

* If you change dependencies, rebuild:

```bash
docker compose build
docker compose up -d
```

* Keep SSH keys and GitHub Secrets up to date.
* Avoid exposing the bot to public networks without proper protection.
