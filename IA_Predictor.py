import requests
import json
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN ---
TOKEN_FUTBOL = '387c7707cc4b4dc1b2fc0f94ae2da4f1'
FIREBASE_URL = 'https://prediccionesfutbol-1199a-default-rtdb.firebaseio.com/'
headers = { 'X-Auth-Token': TOKEN_FUTBOL }

def ejecutar_ia_pro():
    print("⚽ Iniciando IA de Apuestas Avanzada...")
    
    # 1. OBTENER TABLA Y ESTADÍSTICAS
    url_tabla = 'https://api.football-data.org/v4/competitions/PD/standings'
    res_tabla = requests.get(url_tabla, headers=headers).json()
    
    stats_equipos = {}
    for team in res_tabla['standings'][0]['table']:
        nombre = team['team']['name']
        pj = team['playedGames']
        gf = team['goalsFor']
        ga = team['goalsAgainst']
        puntos = team['points']
        racha = team['form'] if team['form'] else "DDDDD"
        
        # Promedios clave
        avg_goles_f = gf / pj
        avg_goles_c = ga / pj
        p_racha = racha.count('W') * 3 + racha.count('D') * 1
        power = (avg_goles_f * 0.6) + (p_racha / 5 * 0.4)
        
        stats_equipos[nombre] = {
            "pwr": round(power, 2),
            "avg_f": avg_goles_f,
            "avg_c": avg_goles_c,
            "escudo": team['team']['crest']
        }

    # 2. ESCANEO Y PREDICCIÓN DETALLADA
    url_partidos = 'https://api.football-data.org/v4/competitions/PD/matches'
    res_partidos = requests.get(url_partidos, headers=headers).json()
    
    predicciones_hoy = []
    for m in res_partidos['matches']:
        if m['status'] in ['SCHEDULED', 'TIMED']:
            loc, vis = m['homeTeam']['name'], m['awayTeam']['name']
            s_l = stats_equipos.get(loc, {"pwr":0, "avg_f":0, "avg_c":0, "escudo":""})
            s_v = stats_equipos.get(vis, {"pwr":0, "avg_f":0, "avg_c":0, "escudo":""})
            
            # LÓGICA DE APUESTAS
            # Ambos Anotan: Si ambos promedian > 1.1 goles o tienen defensas débiles
            btts = "SÍ ✅" if (s_l["avg_f"] > 1.1 and s_v["avg_f"] > 1.1) else "NO ❌"
            
            # Más de 2.5 Goles: Si la suma de ataque/defensa es alta
            total_est = "MÁS DE 2.5 📈" if (s_l["avg_f"] + s_v["avg_f"] > 2.6) else "MENOS DE 2.5 📉"
            
            # Córners: Algoritmo basado en presión ofensiva
            corners = round(8 + (s_l["pwr"] + s_v["pwr"]), 0)

            predicciones_hoy.append({
                "partido": f"{loc} vs {vis}",
                "ganador": loc if s_l["pwr"] > s_v["pwr"] else vis,
                "confianza": "ALTA ⭐" if abs(s_l["pwr"] - s_v["pwr"]) > 0.5 else "MEDIA ⚖️",
                "btts": btts,
                "total_goles": total_est,
                "corners": f"+{int(corners)} Córners",
                "escudo_local": s_l["escudo"],
                "escudo_visitante": s_v["escudo"]
            })

    # 3. SUBIR A FIREBASE
    if predicciones_hoy:
        requests.put(f"{FIREBASE_URL}jornada.json", data=json.dumps(predicciones_hoy))
        print(f"✅ Enviados {len(predicciones_hoy)} partidos con mercados completos.")

if __name__ == "__main__":
    ejecutar_ia_pro()
