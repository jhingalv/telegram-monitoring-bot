import os
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from monitor import get_server_metrics, get_container_status
from alerts import get_active_alerts, get_last_24h_alerts
from alert_engine import check_all_alerts

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))

# /serverstatus
async def server_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    m = get_server_metrics()
    active = get_active_alerts()

    msg = f"""
📊 Estado del Servidor

CPU: {m['cpu']}%
RAM: {m['ram']}%
Disco: {m['disk']}%
Load: {m['load']}

🚨 Alertas activas: {len(active)}
"""
    await update.message.reply_text(msg)

# /dockerstatus
async def docker_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    containers = get_container_status()
    running = [c for c in containers if c["status"] == "running"]

    msg = f"🐳 Contenedores activos: {len(running)}/{len(containers)}\n\n"
    for c in containers:
        msg += f"{c['name']} → {c['status']}\n"

    await update.message.reply_text(msg)

# /alerts
async def alerts_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    active = get_active_alerts()

    if not active:
        await update.message.reply_text("✅ No hay alertas activas")
        return

    msg = "🚨 Alertas vigentes:\n\n"
    for v in active.values():
        msg += f"{v['message']}\nDesde: {v['started_at']}\n\n"

    await update.message.reply_text(msg)

# Daily 10:00 summary
async def daily_summary(chat_id, bot):
    m = get_server_metrics()
    last_alerts = get_last_24h_alerts()

    msg = f"""
📅 Resumen Diario ({datetime.now().date()})

CPU actual: {m['cpu']}%
RAM actual: {m['ram']}%
Disco actual: {m['disk']}%

Alertas últimas 24h: {len(last_alerts)}
"""
    await bot.send_message(chat_id=chat_id, text=msg)

# MAIN
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("serverstatus", server_status))
    app.add_handler(CommandHandler("dockerstatus", docker_status))
    app.add_handler(CommandHandler("alerts", alerts_command))

    # Scheduler
    scheduler = AsyncIOScheduler()
    scheduler.add_job(check_all_alerts, "interval", minutes=2, args=[CHAT_ID, app.bot], id="alert_engine", replace_existing=True)
    scheduler.add_job(daily_summary, "cron", hour=10, minute=0, args=[CHAT_ID, app.bot], id="daily_summary", replace_existing=True)
    scheduler.start()

    app.run_polling()

if __name__ == "__main__":
    main()
