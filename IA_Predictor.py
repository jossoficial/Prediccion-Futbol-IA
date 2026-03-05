import requests
import json
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN ---
TOKEN_FUTBOL = '387c7707cc4b4dc1b2fc0f94ae2da4f1'
FIREBASE_URL = 'https://prediccionesfutbol-1199a-default-rtdb.firebaseio.com/'
headers = { 'X-Auth-Token': TOKEN_FUTBOL }

def ejecutar_ia_maestra():
    print("⚽ Iniciando Analista de IA...")
    
    # 1. OBTENER TABLA Y ESCUDOS
    url_tabla = 'https://api.football-data.org/v4/competitions/PD/standings'
    res_tabla = requests.get(url_tabla, headers=headers).json()
    
    stats_equipos = {}
    for team in res_tabla['standings'][0]['table']:
        nombre = team['team']['name']
        # Fórmula: 60% Tabla + 40% Racha (Momentum)
        racha = team['form'] if team['form'] else "DDDDD"
        p_racha = racha.count('W') * 3 + racha.count('D') * 1
        power = ((team['points']/team['playedGames']) + (team['goalsFor']/team['playedGames'])) * 0.6 + (p_racha/5) * 0.4
        
        stats_equipos[nombre] = {
            "pwr": round(power, 2),
            "escudo": team['team']['crest']
        }

    # 2. ESCANEO DE PARTIDOS
    url_partidos = 'https://api.football-data.org/v4/competitions/PD/matches'
    res_partidos = requests.get(url_partidos, headers=headers).json()
    
    predicciones_hoy = []
    for m in res_partidos['matches']:
        if m['status'] in ['SCHEDULED', 'TIMED']:
            loc, vis = m['homeTeam']['name'], m['awayTeam']['name']
            pwr_l = stats_equipos.get(loc, {"pwr": 0})["pwr"]
            pwr_v = stats_equipos.get(vis, {"pwr": 0})["pwr"]
            
            predicciones_hoy.append({
                "partido": f"{loc} vs {vis}",
                "ganador": loc if pwr_l > pwr_v else vis,
                "confianza": "ALTA ⭐" if abs(pwr_l - pwr_v) > 0.5 else "MEDIA ⚖️",
                "escudo_local": stats_equipos.get(loc, {"escudo": ""})["escudo"],
                "escudo_visitante": stats_equipos.get(vis, {"escudo": ""})["escudo"]
            })

    # 3. ACTUALIZAR FIREBASE
    if predicciones_hoy:
        requests.put(f"{FIREBASE_URL}jornada.json", data=json.dumps(predicciones_hoy))
        alerta = {
            "titulo": "🔥 IA: ¡Predicciones Listas!",
            "mensaje": f"Analizados {len(predicciones_hoy)} partidos. ¡Entra ya!",
            "fecha": datetime.now().strftime("%d/%m %H:%M")
        }
        requests.put(f"{FIREBASE_URL}alerta.json", data=json.dumps(alerta))
        print(f"✅ Éxito: {len(predicciones_hoy)} predicciones enviadas.")
    else:
        print("😴 No hay partidos para hoy.")

if __name__ == "__main__":
    ejecutar_ia_maestra()
