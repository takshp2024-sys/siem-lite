"""
Generates a synthetic /var/log/auth.log-style file with:
  - normal background login traffic (spread across the day, low failure rate)
  - one embedded SSH brute-force burst (>5 failures in <5 min from one IP)
  - one off-hours successful login (03:xx) from an unfamiliar IP

Run: python generate_sample_log.py
     (writes sample_auth.log in the current directory, UTF-8, no shell
     redirection needed — avoids the classic Windows PowerShell issue where
     `> sample_auth.log` silently writes UTF-16 instead of UTF-8)

Optional: python generate_sample_log.py custom_name.log

This gives the SIEM-lite dashboard real signal to detect on a fresh clone,
without needing a live attacker VM.
"""
import random
import sys
from datetime import datetime, timedelta

random.seed(7)

USERS = ["taksh", "deploy", "admin", "backup", "svc_monitor"]
NORMAL_IPS = ["192.168.1.14", "192.168.1.22", "10.0.0.8", "10.0.0.15"]
ATTACKER_IP = "203.0.113.77"
OFF_HOURS_IP = "198.51.100.23"

HOST = "prod-web-01"
MONTH_DAY = datetime.now().strftime("%b %d").split()
MONTH, DAY = MONTH_DAY[0], MONTH_DAY[1]


def fmt(ts: datetime) -> str:
    return ts.strftime(f"{MONTH} {int(DAY):>2} %H:%M:%S")


lines = []
base = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)

# --- Normal background traffic across the day ---
t = base
for _ in range(60):
    t += timedelta(minutes=random.randint(3, 25))
    ip = random.choice(NORMAL_IPS)
    user = random.choice(USERS)
    if random.random() < 0.85:
        lines.append(f"{fmt(t)} {HOST} sshd[{random.randint(1000,9999)}]: Accepted password for {user} from {ip} port {random.randint(30000,60000)} ssh2")
    else:
        lines.append(f"{fmt(t)} {HOST} sshd[{random.randint(1000,9999)}]: Failed password for {user} from {ip} port {random.randint(30000,60000)} ssh2")

# --- Embedded brute-force burst: 9 failures in ~3 minutes from ATTACKER_IP ---
attack_start = base + timedelta(hours=5, minutes=12)
t = attack_start
for i in range(9):
    t += timedelta(seconds=random.randint(10, 25))
    guessed_user = random.choice(["root", "admin", "test", "oracle", "ubuntu"])
    lines.append(f"{fmt(t)} {HOST} sshd[{random.randint(1000,9999)}]: Failed password for invalid user {guessed_user} from {ATTACKER_IP} port {random.randint(30000,60000)} ssh2")

# --- Off-hours successful login (looks like a stolen credential used at 3AM) ---
off_hours_time = base.replace(hour=3, minute=17) + timedelta(days=0)
lines.append(f"{fmt(off_hours_time)} {HOST} sshd[{random.randint(1000,9999)}]: Accepted password for backup from {OFF_HOURS_IP} port {random.randint(30000,60000)} ssh2")

# Sort chronologically like a real log file would be
lines.sort()

output_path = sys.argv[1] if len(sys.argv) > 1 else "sample_auth.log"
with open(output_path, "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(lines) + "\n")

print(f"Wrote {len(lines)} lines to {output_path}")