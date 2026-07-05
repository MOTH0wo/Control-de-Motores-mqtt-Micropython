# Control-de-Motores-mqtt-Micropython

Sistema de control remoto en tiempo real para cuatro motores DC conectados a un ESP32/ Raspberry pi pico 2W, controlado vía MQTT. Un dashboard web (HTML + MQTT.js) publica valores de velocidad (0-255) mediante sliders, y el ESP32 se suscribe directamente al broker para recibir esos comandos y aplicarlos por PWM a cada motor.

El ESP32 se conecta directamente a WiFi y se suscribe al broker por MQTT estándar (puerto 1883). El dashboard web se conecta al **mismo broker** pero por MQTT sobre WebSocket (puerto 8084), que es como los navegadores pueden hablar MQTT sin un puente intermedio.

## Componentes del proyecto

| Archivo | Rol |
|---|---|
| `main.py` | Firmware MicroPython que corre en el ESP32: se suscribe a los tópicos de motores y aplica PWM |
| `dashboard.html` | Panel web standalone con sliders para controlar la velocidad de cada motor en vivo |
| `umqtt/simple.py` | Driver MQTT para MicroPython (dependencia externa, ver más abajo) |

## Hardware necesario

| Componente | Cantidad | Notas |
|---|---|---|
| ESP32 (con WiFi) | 1 | Requiere WiFi para suscribirse directo al broker |
| Motor DC (con driver, ej. L298N/L293D) | 4 | Controlados por PWM |
| Cables / protoboard | — | Para las conexiones |

## Conexiones (ESP32)

| Pin lógico | GPIO | Función |
|---|---|---|
| Motor 1 | 12 | Salida PWM |
| Motor 2 | 13 | Salida PWM |
| Motor 3 | 14 | Salida PWM |
| Motor 4 | 15 | Salida PWM |

> Ajusta los números de pin en `main.py` según tu placa específica. Recuerda que el ESP32 controla el driver de motores (ej. L298N), no el motor directamente.

## Instalación — ESP32 (`main.py`)

1. Flashea el ESP32 con el firmware de MicroPython.
2. Edita en `main.py` las credenciales de tu red:
```python
   WIFI_SSID = "tu_red"
   WIFI_PASSWORD = "tu_password"
```
3. Si tu build de MicroPython no incluye `umqtt.simple`, sube manualmente la carpeta `umqtt/` con `simple.py` al dispositivo.
4. Copia `main.py` a la raíz del sistema de archivos del ESP32 (Thonny, `mpremote`, `ampy`, etc.).
5. Reinicia el ESP32. Si el archivo se llama `main.py`, arranca automáticamente, se suscribe a los cuatro tópicos y queda esperando comandos.
6. Verifica en la consola serial (`print(...)`) que los comandos lleguen y se apliquen correctamente antes de confiar en el dashboard.

## Instalación — Dashboard (`dashboard.html`)

1. Abre `dashboard.html` directamente en cualquier navegador (no necesita servidor, es un archivo standalone).
2. El dashboard se conecta automáticamente al broker `broker.emqx.io` por WebSocket (puerto 8084) al cargar la página.
3. Mueve el slider del motor que quieras controlar (rango 0-255). El valor se publica al tópico correspondiente con un pequeño retraso (debounce de 50ms) para no saturar el broker con cada pixel de movimiento del slider.
4. Verifica el texto de estado en pantalla ("✅ Conectado al broker" / "❌ Error") para confirmar la conexión.

## Tópicos MQTT

| Tópico | Payload | Ejemplo |
|---|---|---|
| `iot/motor1` | Entero como texto plano (0-255) | `"180"` |
| `iot/motor2` | Entero como texto plano (0-255) | `"90"` |
| `iot/motor3` | Entero como texto plano (0-255) | `"255"` |
| `iot/motor4` | Entero como texto plano (0-255) | `"0"` |

## Notas importantes

- **Puertos distintos, mismo broker:** el ESP32 usa MQTT "crudo" por el puerto 1883, mientras que el navegador necesita MQTT sobre WebSocket (puerto 8084) porque los navegadores no pueden abrir sockets TCP directos. Esto es normal y no requiere ningún puente adicional — ambos hablan con el mismo broker público.
- **Broker público:** `broker.emqx.io` es un broker de pruebas gratuito y compartido. Cualquiera que publique en los mismos tópicos (`iot/motor1`, etc.) puede mover tus motores. Para un proyecto en producción o personalizado, se recomienda un broker propio o privado con autenticación.

## Posibles mejoras

- [ ] Broker MQTT propio (Mosquitto local o servicio privado) en vez del público.
- [ ] Autenticación MQTT (usuario/contraseña o certificados TLS).
- [ ] Confirmación de estado: que el ESP32 publique de vuelta el duty aplicado, para que el dashboard muestre feedback real (no solo el valor del slider).
- [ ] Límite de seguridad (rampa de aceleración) para evitar cambios bruscos de velocidad.
- [ ] Reconexión automática de WiFi en el ESP32 si se cae la red (no solo la del broker).
