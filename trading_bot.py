import yfinance as yf
import pandas as pd
import numpy as np
import requests
import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import requests


# Obtener configuración desde variables de entorno
SYMBOL = os.getenv('TRADING_SYMBOL', 'MSTR')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')
MA_PERIOD = int(os.getenv('MA_PERIOD', '200'))  # Período para la media móvil
YEARS_OF_DATA = int(os.getenv('YEARS_OF_DATA', '10'))  # Años de datos históricos a obtener


def enviar_imagen_telegram(token, chat_id, path_imagen, caption=""):
    """Envía una imagen al chat de Telegram"""
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    with open(path_imagen, 'rb') as image_file:
        files = {'photo': image_file}
        data = {'chat_id': chat_id, 'caption': caption}
        response = requests.post(url, files=files, data=data)
    
    if response.status_code == 200:
        print("Imagen enviada exitosamente por Telegram.")
    else:
        print(f"Error al enviar imagen: {response.status_code} - {response.text}")




def generar_grafico(datos, nombre_archivo='grafico.png'):
    """Genera un gráfico del precio y la media móvil y lo guarda como imagen"""
    plt.figure(figsize=(14, 7))
    plt.plot(datos.index, datos['Close'], label='Precio de Cierre', color='blue')
    plt.plot(datos.index, datos['MA200'], label=f'Media Móvil {MA_PERIOD} días', color='red', linestyle='--')
    plt.title(f'{SYMBOL} - Precio vs MA{MA_PERIOD}')
    plt.xlabel('Fecha')
    plt.ylabel('Precio (USD)')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(nombre_archivo)
    plt.close()
    print(f"Gráfico guardado como {nombre_archivo}")
    return nombre_archivo


def obtener_datos_financieros():
    """Obtiene los datos financieros del símbolo especificado"""
    fecha_fin = datetime.now()
    fecha_inicio = fecha_fin - timedelta(days=365 * YEARS_OF_DATA)
    
    print(f"Obteniendo datos desde {fecha_inicio.strftime('%Y-%m-%d')} hasta {fecha_fin.strftime('%Y-%m-%d')}")
    datos = yf.download(SYMBOL, start=fecha_inicio, end=fecha_fin)
    
    if datos.empty:
        print(f"No se pudieron obtener datos para {SYMBOL}")
        return pd.DataFrame()
    
    print(f"Se obtuvieron {len(datos)} días de datos")
    print(f"Columnas originales: {datos.columns.tolist()}")
    
    # --- FIX PARA MULTIINDEX ---
    if isinstance(datos.columns, pd.MultiIndex):
        print("Detectado MultiIndex en columnas. Simplificando...")
        # Solo nos quedamos con el primer nivel (ejemplo: 'Close')
        datos.columns = datos.columns.get_level_values(0)
    
    print(f"Columnas después de simplificar: {datos.columns.tolist()}")
    
    df_procesado = datos.copy()
    
    if len(df_procesado) < MA_PERIOD:
        print(f"Advertencia: Solo hay {len(df_procesado)} días de datos, insuficientes para calcular MA{MA_PERIOD}")
        df_procesado['MA200'] = np.nan
    else:
        print(f"Calculando media móvil de {MA_PERIOD} períodos...")
        df_procesado['MA200'] = df_procesado['Close'].rolling(window=MA_PERIOD).mean()
        print("Media móvil calculada correctamente.")
    
    return df_procesado

    
    return df_procesado

def verificar_condiciones(datos):
    """Verifica si se cumplen las condiciones para enviar el mensaje"""
    if 'MA200' not in datos.columns:
        print("No se encontró la columna 'MA200'. No se puede verificar condiciones.")
        return False, {}
    
    datos_filtrados = datos.dropna(subset=['MA200'])
    
    if len(datos_filtrados) < 3:
        print(f"No hay suficientes datos con MA200 calculada. Solo {len(datos_filtrados)} días disponibles.")
        return False, {}
    
    ultimos_datos = datos_filtrados.tail(3)
    
    print(f"Análisis de los últimos 3 días con MA200:")
    print(ultimos_datos[['Close', 'MA200']])
    
    precios = ultimos_datos['Close'].values
    medias = ultimos_datos['MA200'].values
    
    precio_actual = precios[-1]
    ma_actual = medias[-1]
    
    condicion1 = precio_actual < ma_actual
    
    dia1 = precios[0] > medias[0]
    dia2 = precios[1] < medias[1]
    dia3 = precios[2] > medias[2]
    condicion2 = dia1 and dia2 and dia3
    
    diferencia_porcentual = (precio_actual - ma_actual) / ma_actual * 100
    condicion3 = 0 < diferencia_porcentual < 1.0
    
    condicion4 = abs(precio_actual - ma_actual) < 0.001
    
    print(f"Precio actual: ${precio_actual:.2f} | MA200: ${ma_actual:.2f}")
    print(f"Condición 1 (precio < MA200): {condicion1}")
    print(f"Condición 2 (cruce hacia arriba): {condicion2}")
    print(f"Condición 3 (precio <1% sobre MA200): {condicion3}")
    print(f"Condición 4 (precio ≈ MA200): {condicion4}")
    
    return any([condicion1, condicion2, condicion3, condicion4]), {
        "precio_actual": precio_actual,
        "ma_actual": ma_actual,
        "condicion1": condicion1,
        "condicion2": condicion2,
        "condicion3": condicion3,
        "condicion4": condicion4
    }

def enviar_mensaje_telegram(detalles):
    """Envía un mensaje a Telegram con los detalles de la alerta"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("No se configuraron las credenciales de Telegram. No se enviará mensaje.")
        return False
    
    precio = detalles["precio_actual"]
    ma = detalles["ma_actual"]
    
    mensaje = f"🚨 ALERTA {SYMBOL} 🚨\n\n"
    mensaje += f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    mensaje += f"Símbolo: {SYMBOL}\n"
    mensaje += f"Precio actual: ${precio:.2f}\n"
    mensaje += f"Media Móvil {MA_PERIOD}: ${ma:.2f}\n\n"
    
    if detalles["condicion1"]:
        mensaje += "⚠️ El precio está por debajo de la media móvil\n"
    if detalles["condicion2"]:
        mensaje += "🔼 Se detectó un cruce hacia arriba\n"
    if detalles["condicion3"]:
        mensaje += "⚖️ El precio está a menos del 1% por encima de la media móvil\n"
    if detalles["condicion4"]:
        mensaje += "🎯 El precio coincide exactamente con la media móvil\n"
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensaje,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print("Mensaje enviado con éxito a Telegram")
            return True
        else:
            print(f"Error al enviar mensaje: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Excepción al enviar mensaje: {str(e)}")
        return False

def test_telegram():
    """Función para probar la conexión con Telegram"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("No se configuraron las credenciales de Telegram")
        return False
    
    mensaje = f"🧪 Mensaje de prueba desde el bot de trading {SYMBOL} 🧪\nFecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensaje
    }
    
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print("✅ Conexión con Telegram exitosa")
            return True
        else:
            print(f"❌ Error al conectar con Telegram: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Excepción: {str(e)}")
        return False

def main():
    print(f"[{datetime.now()}] Iniciando análisis para {SYMBOL}...")
    
    datos = obtener_datos_financieros()
    
    if datos.empty:
        print("No se pudieron obtener datos. Finalizando.")
        return
    
    cumple_condiciones, detalles = verificar_condiciones(datos)
    
    if cumple_condiciones and detalles:
        print("¡Se cumplen las condiciones! Enviando mensaje a Telegram...")
        enviar_mensaje_telegram(detalles)
        nombre_grafico = generar_grafico(datos)
        enviar_imagen_telegram(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, nombre_grafico, caption=f"Gráfico de {SYMBOL}")

    else:
        print("No se cumplen las condiciones para enviar alerta.")
    
    if detalles:
        print(f"Resumen final:")
        print(f"Precio actual: ${detalles['precio_actual']:.2f}")
        print(f"MA {MA_PERIOD}: ${detalles['ma_actual']:.2f}")
    
    print(f"[{datetime.now()}] Análisis completado.")
        # 1. Generar el gráfico



if __name__ == "__main__":
   # test_telegram()  # Descomenta para probar Telegram
    main()
