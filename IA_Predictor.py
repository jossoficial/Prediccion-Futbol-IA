import requests
import json
import pandas as pd
from datetime import datetime

# --- TUS CREDENCIALES ---
TOKEN_FUTBOL = '387c7707cc4b4dc1b2fc0f94ae2da4f1'
FIREBASE_URL = 'https://prediccionesfutbol-1199a-default-rtdb.firebaseio.com/'
headers = { 'X-Auth-Token': TOKEN_FUTBOL }

def ejecutar_ia_maestra():
    print("⚽ Iniciando Analista de IA...")
    
    # 1. OBTENER TABLA Y MOMENTUM (RACHA)
    url_tabla = 'https://api.football-data.org/v4/competitions/PD/standings'
    res_tabla = requests.get(url_tabla, headers=headers).json()
    
    stats_equipos = {}
    for team in res_tabla['standings'][0]['table']:
        nombre = team['team']['name']
        puntos = team['points']
        pj = team['playedGames']
        goles = team['goalsFor']
        racha = team['form'] if team['form'] else "DDDDD" # W=Gana, D=Empata, L=Pierde
        
        # Valor de Racha (W=3, D=1, L=0)
        puntos_racha = racha.count('W') * 3 + racha.count('D') * 1
        
        # FÓRMULA: 60% Tabla Histórica + 40% Racha Reciente
        power = ((puntos/pj) + (goles/pj)) * 0.6 + (puntos_racha/5) * 0.4
        stats_equipos[nombre] = {
            "pwr": round(power, 2),
            "escudo": team['team']['crest'] # URL del escudo oficial
        }

    # 2. BUSCAR PARTIDOS DE HOY AUTOMÁTICAMENTE
    url_partidos = 'https://api.football-data.org/v4/competitions/PD/matches'
    res_partidos = requests.get(url_partidos, headers=headers).json()
    
    predicciones_del_dia = []
    
    for m in res_partidos['matches']:
        # Solo partidos por jugar (SCHEDULED)
        if m['status'] in ['SCHEDULED', 'TIMED']:
            loc_name = m['homeTeam']['name']
            vis_name = m['awayTeam']['name']
            
            # Obtener datos de nuestra IA
            pwr_l = stats_equipos.get(loc_name, {"pwr": 0})["pwr"]
            pwr_v = stats_equipos.get(vis_name, {"pwr": 0})["pwr"]
            escudo_l = stats_equipos.get(loc_name, {"escudo": ""})["escudo"]
            escudo_v = stats_equipos.get(vis_name, {"escudo": ""})["escudo"]
            
            # Decisión de la IA
            ganador = loc_name if pwr_l > pwr_v else vis_name
            dif = abs(pwr_l - pwr_v)
            confianza = "ALTA" if dif > 0.5 else "MEDIA"
            
            predicciones_del_dia.append({
                "partido": f"{loc_name} vs {vis_name}",
                "ganador": ganador,
                "confianza": confianza,
                "escudo_local": escudo_l,
                "escudo_visitante": escudo_v,
                "hora": m['utcDate']
            })

    # 3. ENVIAR A FIREBASE Y DISPARAR NOTIFICACIÓN
    if predicciones_del_dia:
        # Subir lista completa
        requests.put(f"{FIREBASE_URL}jornada.json", data=json.dumps(predicciones_del_dia))
        
        # Enviar señal de notificación a la App
        alerta = {
            "titulo": "🔥 IA: ¡Predicciones Listas!",
            "mensaje": f"Analizados {len(predicciones_del_dia)} partidos de hoy con éxito.",
            "fecha": datetime.now().strftime("%d/%m/%Y %H:%M")
        }
        requests.put(f"{FIREBASE_URL}alerta.json", data=json.dumps(alerta))
        print(f"✅ ¡Éxito! {len(predicciones_del_dia)} partidos enviados a Firebase.")
    else:
        print("😴 Hoy no hay partidos programados en La Liga.")

# Ejecutar programa
ejecutar_ia_maestra()
