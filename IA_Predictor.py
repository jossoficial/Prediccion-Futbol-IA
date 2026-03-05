import requests
import json
import pandas as pd

# Configuración de APIs
TOKEN_FUTBOL = '387c7707cc4b4dc1b2fc0f94ae2da4f1'
FIREBASE_URL = 'https://prediccionesfutbol-1199a-default-rtdb.firebaseio.com/predicciones.json'

def ejecutar_prediccion(local, visitante):
    headers = { 'X-Auth-Token': TOKEN_FUTBOL }
    url = 'https://api.football-data.org/v4/competitions/PD/standings'
    res = requests.get(url, headers=headers).json()
    
    # Procesar tabla de posiciones
    equipos = []
    for team in res['standings'][0]['table']:
        equipos.append({
            'nombre': team['team']['name'],
            'puntos': team['points'],
            'goles': team['goalsFor'],
            'pj': team['playedGames']
        })
    df = pd.DataFrame(equipos)
    
    # Lógica de cálculo (IA simple)
    stats_l = df[df['nombre'] == local].iloc[0]
    stats_v = df[df['nombre'] == visitante].iloc[0]
    
    pow_l = (stats_l['puntos'] / stats_l['pj']) + (stats_l['goles'] / stats_l['pj'])
    pow_v = (stats_v['puntos'] / stats_v['pj']) + (stats_v['goles'] / stats_v['pj'])
    
    ganador = local if pow_l > pow_v else visitante
    
    # Enviar datos a Firebase para la App
    datos = {
        "partido": f"{local} vs {visitante}",
        "ganador": ganador,
        "score_l": round(pow_l, 2),
        "score_v": round(pow_v, 2)
    }
    requests.put(FIREBASE_URL, data=json.dumps(datos))
    print(f"✅ Predicción enviada a Firebase: {ganador}")

# Ejemplo de ejecución
ejecutar_prediccion('Real Madrid CF', 'FC Barcelona')
