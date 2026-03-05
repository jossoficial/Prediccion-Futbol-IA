import requests
import json
import pandas as pd
from datetime import datetime

# CONFIGURACIÓN
TOKEN_FUTBOL = '387c7707cc4b4dc1b2fc0f94ae2da4f1'
FIREBASE_URL = 'https://prediccionesfutbol-1199a-default-rtdb.firebaseio.com/jornada_hoy.json'
headers = { 'X-Auth-Token': TOKEN_FUTBOL }

def automatizar_jornada():
    # 1. Obtener la tabla para tener las estadísticas de poder
    url_tabla = 'https://api.football-data.org/v4/competitions/PD/standings'
    res_tabla = requests.get(url_tabla, headers=headers).json()
    
    equipos_stats = {}
    for team in res_tabla['standings'][0]['table']:
        # Calculamos el Power Score (Puntos + Goles / Partidos Jugados)
        power = (team['points'] / team['playedGames']) + (team['goalsFor'] / team['playedGames'])
        equipos_stats[team['team']['name']] = round(power, 2)

    # 2. Buscar los partidos programados para HOY
    url_partidos = 'https://api.football-data.org/v4/competitions/PD/matches'
    res_partidos = requests.get(url_partidos, headers=headers).json()
    
    predicciones_hoy = []
    
    for match in res_partidos['matches']:
        # Filtramos solo partidos que no han empezado (SCHEDULED o TIMED)
        if match['status'] in ['SCHEDULED', 'TIMED']:
            local = match['homeTeam']['name']
            visitante = match['awayTeam']['name']
            
            # Obtenemos sus poderes de nuestra tabla
            p_local = equipos_stats.get(local, 0)
            p_visitante = equipos_stats.get(visitante, 0)
            
            ganador = local if p_local > p_visitante else visitante
            
            predicciones_hoy.append({
                'partido': f"{local} vs {visitante}",
                'prediccion': ganador,
                'hora': match['utcDate']
            })

    # 3. Enviar toda la lista a Firebase
    if predicciones_hoy:
        requests.put(FIREBASE_URL, data=json.dumps(predicciones_hoy))
        print(f"✅ Se han enviado {len(predicciones_hoy)} predicciones a tu App.")
    else:
        print("⚽ No hay partidos programados para hoy.")

# Ejecutar el piloto automático
automatizar_jornada()
