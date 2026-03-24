import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta

print("🚀 Generando calendario de Racing...")

url = "https://www.promiedos.com.ar/team/racing-club/ihg"
headers = {"User-Agent": "Mozilla/5.0"}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

# Extraer JSON de Promiedos
script = soup.find("script", {"id": "__NEXT_DATA__"})
data = json.loads(script.string)

games_data = data["props"]["pageProps"]["data"]["games"]

# Unimos futuros + pasados
rows = games_data["next"]["rows"] + games_data["last"]["rows"]

# Timestamp global (UTC)
now = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

# Base del archivo ICS (CON TIMEZONE)
ics_content = """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//Racing Fixture//EN
BEGIN:VTIMEZONE
TZID:America/Argentina/Buenos_Aires
BEGIN:STANDARD
TZOFFSETFROM:-0300
TZOFFSETTO:-0300
TZNAME:-03
DTSTART:19700101T000000
END:STANDARD
END:VTIMEZONE
"""

for r in rows:
    game = r["game"]
    
    start = game.get("start_time")
    if not start:
        continue
    
    try:
        dt_obj = datetime.strptime(start, "%d-%m-%Y %H:%M")
    except:
        continue

    # Formato correcto
    dt_start = dt_obj.strftime("%Y%m%dT%H%M%S")
    dt_end = (dt_obj + timedelta(hours=2)).strftime("%Y%m%dT%H%M%S")

    # UID único
    uid = game.get("id") + "@racing-fixture"

    # Equipos
    teams = game["teams"]
    team1 = teams[0]["name"]
    team2 = teams[1]["name"]

    if "Racing" in team1:
        title = f"Racing vs {team2}"
    else:
        title = f"{team1} vs Racing"

    description = game.get("stage_round_name", "")

    # Evento (CON TZID)
    ics_content += f"""BEGIN:VEVENT
UID:{uid}
DTSTAMP:{now}
SUMMARY:{title}
DTSTART;TZID=America/Argentina/Buenos_Aires:{dt_start}
DTEND;TZID=America/Argentina/Buenos_Aires:{dt_end}
DESCRIPTION:{description}
END:VEVENT
"""

ics_content += "END:VCALENDAR"

# Guardar archivo
with open("racing.ics", "w", encoding="utf-8") as f:
    f.write(ics_content)

print("✅ Archivo racing.ics generado correctamente")