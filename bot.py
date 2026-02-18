import os
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler

from monitor import get_server_metrics, get_container_status
from alerts import get_active_alerts, get_last_24h_alerts
from alert_engine import check_all_alerts

import asyncio

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))

# --- Telegram Commands ---
async def server_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    m = get_server_metrics()
    active = get_active_alerts()
    msg = f"""
📊 Server Status

 - CPU use: {m['cpu']}%
 - RAM use: {m['ram']}%
 - Disk use: {m['disk']}%

🚨 Active Alerts: {len(active)}
"""
    await update.message.reply_text(msg)

async def docker_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    containers = get_container_status()
    running = [c for c in containers if c["status"] == "running"]
    msg = f"🐳 Active containers: {len(running)}/{len(containers)}\n\n"
    for c in containers:
        msg += f"{c['name']} → {c['status']}\n"
    await update.message.reply_text(msg)

async def alerts_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    active = get_active_alerts()
    if not active:
        await update.message.reply_text("✅ No active alerts")
        return
    msg = "⚠️ Current Alerts:\n\n"
    for v in active.values():
        msg += f"{v['message']}\nSince: {v['started_at']}\n\n"
    await update.message.reply_text(msg)

# --- Daily summary ---
async def daily_summary(chat_id, bot):
    m = get_server_metrics()
    last_alerts = get_last_24h_alerts()
    msg = f"""
📅 Daily Brief ({datetime.now().date()})

 - CPU use: {m['cpu']}%
 - RAM use: {m['ram']}%
 - Disk use: {m['disk']}%

⚠️ Alerts in the last 24h: {len(last_alerts)}
"""
    await bot.send_message(chat_id=chat_id, text=msg)

# --- MAIN ---
def main():

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("serverstatus", server_status))
    app.add_handler(CommandHandler("dockerstatus", docker_status))
    app.add_handler(CommandHandler("alerts", alerts_command))

    scheduler = BackgroundScheduler()

    scheduler.add_job(lambda: asyncio.run(check_all_alerts(CHAT_ID, app.bot)),
                      "interval", minutes=1, id="alert_engine", replace_existing=True)

    scheduler.add_job(lambda: asyncio.run(daily_summary(CHAT_ID, app.bot)),
                      "cron", hour=10, minute=0, id="daily_summary", replace_existing=True)

    scheduler.start()

    app.run_polling()

if __name__ == "__main__":
    main()
