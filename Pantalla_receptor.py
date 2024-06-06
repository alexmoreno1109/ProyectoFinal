import board
import busio
import digitalio
import time
import adafruit_ssd1306

# Configurar la comunicación UART (TX: Pin 4, RX: Pin 5)
uart = busio.UART(board.GP4, board.GP5, baudrate=9600)

# Configurar el pin LED
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

# Configurar la comunicación I2C para la pantalla OLED
i2c = busio.I2C(board.GP17, board.GP16)
oled = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)

# Loop principal
while True:
    try:
        # Leer el mensaje completo desde UART
        mensaje1 = uart.readline()
        mensaje2 = uart.readline()
        
        # Verificar si se recibió un mensaje
        if mensaje1 is not None and mensaje2 is not None:
            # Imprimir los mensajes en la consola
            print("Mensaje 1:", mensaje1)
            print("Mensaje 2:", mensaje2)
            
            # Limpiar la pantalla OLED
            oled.fill(0)
            
            # Dibujar los textos en la pantalla OLED
            oled.text(mensaje1.decode('utf-8').strip(), 0, 0, 1)
            oled.text(mensaje2.decode('utf-8').strip(), 0, 10, 1)  # Colocar el segundo dato debajo del primero
            
            # Actualizar la pantalla OLED con los textos
            oled.show()
            
            # Encender el LED al recibir datos
            led.value = True

            # Esperar un momento antes de apagar el LED
            time.sleep(0.1)
            led.value = False
    except KeyboardInterrupt:
        break

# Cerrar la conexión UART al salir
uart.deinit()
