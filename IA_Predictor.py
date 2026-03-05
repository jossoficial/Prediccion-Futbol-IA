import requests
import json
import pandas as pd

# CONFIGURACIÓN
TOKEN_FUTBOL = '387c7707cc4b4dc1b2fc0f94ae2da4f1'
FIREBASE_URL = 'https://prediccionesfutbol-1199a-default-rtdb.firebaseio.com/predicciones.json'
headers = { 'X-Auth-Token': TOKEN_FUTBOL }

def calcular_con_racha(local, visitante):
    # 1. Obtener la tabla y los últimos resultados
    url_tabla = 'https://api.football-data.org/v4/competitions/PD/standings'
    data = requests.get(url_tabla, headers=headers).json()
    
    equipos = []
    for team in data['standings'][0]['table']:
        # Extraemos la racha (ejemplo: W,D,L,W,W)
        racha = team['form'] if team['form'] else "DDDDD" 
        
        # Convertimos la racha en un valor numérico (W=3 pts, D=1 pt, L=0 pts)
        puntos_racha = racha.count('W') * 3 + racha.count('D') * 1
        
        equipos.append({
            'nombre': team['team']['name'],
            'puntos': team['points'],
            'goles': team['goalsFor'],
            'pj': team['playedGames'],
            'racha_valor': puntos_racha # El "Momentum"
        })
    
    df = pd.DataFrame(equipos)
    
    # 2. Lógica Avanzada (60% Historia + 40% Racha Actual)
    def obtener_power(nombre_equipo):
        e = df[df['nombre'] == nombre_equipo].iloc[0]
        base = (e['puntos'] / e['pj']) + (e['goles'] / e['pj'])
        momentum = (e['racha_valor'] / 5) # Promedio de los últimos 5
        return (base * 0.6) + (momentum * 0.4)

    power_l = obtener_power(local)
    power_v = obtener_power(visitante)
    
    ganador = local if power_l > power_v else visitante
    
    # 3. Enviar a Firebase con el nuevo nivel de confianza
    datos = {
        "partido": f"{local} vs {visitante}",
        "ganador": ganador,
        "confianza": round(abs(power_l - power_v) * 10, 2), # Diferencia de nivel
        "analisis": "Basado en racha de últimos 5 partidos"
    }
    
    requests.put(FIREBASE_URL, data=json.dumps(datos))
    print(f"🔥 IA Mejorada: {ganador} tiene mejor racha actual.")

# Prueba con el próximo partido
calcular_con_racha('Real Madrid CF', 'FC Barcelona')
