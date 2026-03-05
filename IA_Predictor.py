import requests
import json
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN DE TUS LLAVES ---
TOKEN_FUTBOL = '387c7707cc4b4dc1b2fc0f94ae2da4f1'
FIREBASE_URL = 'https://prediccionesfutbol-1199a-default-rtdb.firebaseio.com/'
headers = { 'X-Auth-Token': TOKEN_FUTBOL }

def ejecutar_ia_profesional():
    print("🚀 Iniciando Escaneo de Jornada...")
    
    # 1. OBTENER ESTADÍSTICAS Y RACHAS
    url_tabla = 'https://api.football-data.org/v4/competitions/PD/standings'
    res_tabla = requests.get(url_tabla, headers=headers).json()
    
    stats_equipos = {}
    for team in res_tabla['standings'][0]['table']:
        nombre = team['team']['name']
        puntos = team['points']
        pj = team['playedGames']
        goles = team['goalsFor']
        racha = team['form'] if team['form'] else "DDDDD"
        
        # Cálculo de Momentum (W=3, D=1, L=0)
        valor_racha = racha.count('W') * 3 + racha.count('D') * 1
        
        # FÓRMULA IA: (60% Historia/Puntos + 40% Racha Actual)
        power_score = ((puntos/pj) + (goles/pj)) * 0.6 + (valor_racha/5) * 0.4
        stats_equipos[nombre] = round(power_score, 2)

    # 2. BUSCAR PARTIDOS DE HOY AUTOMÁTICAMENTE
    url_partidos = 'https://api.football-data.org/v4/competitions/PD/matches'
    res_partidos = requests.get(url_partidos, headers=headers).json()
    
    predicciones_finales = []
    
    for m in res_partidos['matches']:
        # Solo partidos programados para hoy o próximos
        if m['status'] in ['SCHEDULED', 'TIMED']:
            loc = m['homeTeam']['name']
            vis = m['awayTeam']['name']
            
            pwr_l = stats_equipos.get(loc, 0)
            pwr_v = stats_equipos.get(vis, 0)
            
            ganador = loc if pwr_l > pwr_v else vis
            confianza = round(abs(pwr_l - pwr_v) * 10, 1)
            
            predicciones_finales.append({
                "partido": f"{loc} vs {vis}",
                "prediccion": ganador,
                "confianza": f"{confianza}%",
                "hora": m['utcDate']
            })

    # 3. ACTUALIZAR FIREBASE Y ENVIAR NOTIFICACIÓN
    if predicciones_finales:
        # Subir lista de partidos
        requests.put(f"{FIREBASE_URL}jornada.json", data=json.dumps(predicciones_finales))
        
        # Enviar señal de Alerta/Notificación
        alerta = {
            "titulo": "⚽ ¡IA Actualizada!",
            "mensaje": f"Se han analizado {len(predicciones_finales)} partidos con éxito.",
            "hora": datetime.now().strftime("%H:%M")
        }
        requests.put(f"{FIREBASE_URL}alerta.json", data=json.dumps(alerta))
        
        print(f"✅ ÉXITO: {len(predicciones_finales)} predicciones enviadas a la App.")
    else:
        print("😴 No hay partidos programados para las próximas horas.")

# --- EJECUTAR TODO ---
ejecutar_ia_profesional()
