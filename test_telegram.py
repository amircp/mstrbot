import requests
from datetime import datetime

# Credenciales de Telegram
TELEGRAM_BOT_TOKEN = "7643440132:AAHRHhbUg4EokP5kRQRLg1NfpRu6pf8wTPQ"
TELEGRAM_CHAT_ID = "-1002531086470"

def enviar_mensaje_simulacion():
    """Envía un mensaje de prueba simulando una alerta de trading"""
    
    # Datos de simulación
    symbol = "MSTR"
    precio_actual = 1256.78
    ma_actual = 1242.50
    
    # Construir mensaje
    mensaje = f"🚨 ALERTA {symbol} (SIMULACIÓN) 🚨\n\n"
    mensaje += f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    mensaje += f"Símbolo: {symbol}\n"
    mensaje += f"Precio actual: ${precio_actual:.2f}\n"
    mensaje += f"Media Móvil 200: ${ma_actual:.2f}\n\n"
    
    # Condiciones simuladas (todas verdaderas para mostrar todos los casos)
    mensaje += "⚠️ SIMULACIÓN: El precio está por debajo de la media móvil de 200 días\n"
    mensaje += "🔼 SIMULACIÓN: Se detectó un cruce hacia arriba después de estar por debajo de la media\n"
    mensaje += "⚖️ SIMULACIÓN: El precio está a menos del 1% por encima de la media móvil\n"
    mensaje += "🎯 SIMULACIÓN: El precio coincide exactamente con la media móvil\n\n"
    
    mensaje += "✅ Este es un mensaje de prueba para verificar la configuración del bot."
    
    # URL para la API de Telegram
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    # Datos para la solicitud
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensaje,
        "parse_mode": "HTML"
    }
    
    # Enviar solicitud a la API de Telegram
    try:
        print("Enviando mensaje de prueba a Telegram...")
        response = requests.post(url, data=data)
        
        if response.status_code == 200:
            print("✅ Mensaje enviado con éxito")
            print("Respuesta del servidor:", response.json())
            return True
        else:
            print(f"❌ Error al enviar mensaje: {response.status_code}")
            print("Respuesta del servidor:", response.text)
            return False
    except Exception as e:
        print(f"❌ Excepción al enviar mensaje: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== Script de prueba para notificaciones de trading ===")
    resultado = enviar_mensaje_simulacion()
    if resultado:
        print("✅ Prueba completada con éxito")
    else:
        print("❌ La prueba falló")
