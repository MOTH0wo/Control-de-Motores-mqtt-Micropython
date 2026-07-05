from machine import Pin, PWM
from umqtt.simple import MQTTClient
import network
import time

# Configuración WiFi
WIFI_SSID = "tu_red"
WIFI_PASSWORD = "tu_password"

# Configuración MQTT
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_CLIENT_ID = "esp32_motores"

TOPICS = [b"iot/motor1", b"iot/motor2", b"iot/motor3", b"iot/motor4"]

# Configuracion de motores
motor1 = PWM(Pin(12), freq=1000)
motor2 = PWM(Pin(13), freq=1000)
motor3 = PWM(Pin(14), freq=1000)
motor4 = PWM(Pin(15), freq=1000)

MOTORES = {
    b"iot/motor1": motor1,
    b"iot/motor2": motor2,
    b"iot/motor3": motor3,
    b"iot/motor4": motor4,
}

def velocidad_a_duty(valor):
    return int((valor / 255) * 1023)

def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Conectando a WiFi...")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        while not wlan.isconnected():
            time.sleep(0.5)
    print("WiFi conectada:", wlan.ifconfig())

def on_message(topic, msg):
    print("Topic:", topic, "| Valor:", msg)
    motor = MOTORES.get(topic)
    if motor is None:
        return
    try:
        valor = int(msg)
        duty = velocidad_a_duty(valor)
        motor.duty(duty)
        print(topic.decode(), "duty:", duty)
    except ValueError:
        print("Valor inválido recibido:", msg)

def conectar_mqtt():
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
    client.set_callback(on_message)
    client.connect()
    for topic in TOPICS:
        client.subscribe(topic)
        print("Suscrito al topic:", topic.decode())
    print("Conectado al broker MQTT")
    return client

conectar_wifi()
client = conectar_mqtt()

print("ESP32 lista, esperando comandos...")

while True:
    try:
        client.wait_msg()
    except Exception as ex:
        print("Error MQTT, reconectando:", ex)
        try:
            client.disconnect()
        except:
            pass
        client = None
        while client is None:
            try:
                client = conectar_mqtt()
            except Exception as ex2:
                print("No se pudo reconectar:", ex2)
                time.sleep(5)
