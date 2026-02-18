from alerts import trigger_alert, resolve_alert
from monitor import get_server_metrics, get_container_status

CPU_WARNING = 80
RAM_WARNING = 85
DISK_WARNING = 85

async def check_all_alerts(chat_id, bot):
    metrics = get_server_metrics()

    # --- CPU ---
    if metrics["cpu"] > CPU_WARNING:
        msg = trigger_alert("cpu_high", f"📊🚨 High CPU usage: {metrics['cpu']}%")
        if msg:
            await bot.send_message(chat_id=chat_id, text=msg)
            print(f"CPU alert sent: {msg}")
    else:
        resolved = resolve_alert("cpu_high")
        if resolved:
            await bot.send_message(chat_id=chat_id, text=resolved)
            print(f"CPU alert resolved: {resolved}")

    # --- RAM ---
    if metrics["ram"] > RAM_WARNING:
        msg = trigger_alert("ram_high", f"📊🚨 High RAM usage: {metrics['ram']}%")
        if msg:
            await bot.send_message(chat_id=chat_id, text=msg)
            print(f"RAM alert sent: {msg}")
    else:
        resolved = resolve_alert("ram_high")
        if resolved:
            await bot.send_message(chat_id=chat_id, text=resolved)
            print(f"RAM alert resolved: {resolved}")

    # --- DISK ---
    if metrics["disk"] > DISK_WARNING:
        msg = trigger_alert("disk_high", f"📊🚨 High DISK usage: {metrics['disk']}%")
        if msg:
            await bot.send_message(chat_id=chat_id, text=msg)
            print(f"Disk alert sent: {msg}")
    else:
        resolved = resolve_alert("disk_high")
        if resolved:
            await bot.send_message(chat_id=chat_id, text=resolved)
            print(f"Disk alert resolved: {resolved}")

    # --- CONTAINERS ---
    containers = get_container_status()
    for c in containers:
        key = f"container_{c['name']}"
        if c["status"] != "running":
            msg = trigger_alert(
                key,
                f"🐳🚨 Container error: {c['name']} ({c['status']})"
            )
            if msg:
                await bot.send_message(chat_id=chat_id, text=msg)
                print(f"Container alert sent: {msg}")
        else:
            resolved = resolve_alert(key)
            if resolved:
                await bot.send_message(chat_id=chat_id, text=resolved)
                print(f"Container alert resolved: {resolved}")
