import psutil
import smtplib
import json
import socket
from email.mime_text import MIMEText
from datetime import datetime

CONFIG_PATH = "/opt/sys_monitor/config.json"

def load_config():
    """Load configuration from JSON file."""
    with open(CONFIG_PATH) as f:
        return json.load(f)

def get_metrics():
    """Get current system metrics."""
    return {
        "cpu": psutil.cpu_percent(interval=1),
        "ram": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage("/").percent,
        "net": psutil.net_io_counters().bytes_sent
               + psutil.net_io_counters().bytes_recv,
    }

def send_email(config, subject, body):
    """Send an email using SMTP settings from config."""
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = config["smtp_user"]
    msg["To"] = ",".join(config["recipients"])

    with smtplib.SMTP(config["smtp_server"], config["smtp_port"]) as server:
        server.starttls()
        server.login(config["smtp_user"], config["smtp_password"])
        server.send_message(msg)

def main():

    config = load_config()
    metrics = get_metrics()
    alerts = []

    print("------ System Metrics ------")
    for key, value in metrics.items():
        print(f"{key.upper()}: {value}")
    print("----------------------------")

    for key, value in metrics.items():
        if value > config["thresholds"].get(key, 90):
            alerts.append(f"{key.upper()} usage high: {value}")

    if alerts:
        hostname = socket.gethostname()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        body = (
            f"Linux System Monitor Alert on {hostname}\n"
            f"Time: {now}\n\n" +
            "\n".join(alerts)
        )
        send_email(config, "[ALERT] System Resource Usage", body)

        print("ALERT TRIGGERED:")
        for line in alerts:
            print(line)
    else:
        print("No alerts triggered. All metrics within thresholds.")

if __name__ == "__main__":
    main()
