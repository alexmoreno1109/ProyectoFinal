import sys
import time
import pwmio
import digitalio
import busio
import board

vel_ini_derecha=65;
vel_ini_izquierda=65;
uart = busio.UART(board.GP16, board.GP17, baudrate=9600)
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT
pwm_derecha = pwmio.PWMOut(board.GP20,frequency=100000, duty_cycle=0)
pwm_izquierda = pwmio.PWMOut(board.GP21,frequency=100000, duty_cycle=0)

pwm_derecha.duty_cycle = 0
pwm_izquierda.duty_cycle = 0

pin_motor_derecha=board.GP10
pin_motor_izquierda=board.GP11
pin_ledblanco=board.GP22
# Configurar el pin como salida
motor_d = digitalio.DigitalInOut(pin_motor_derecha)
motor_d.direction = digitalio.Direction.OUTPUT

# Establecer el pin en alto
motor_d.value = True

# Configurar el pin como salida
motor_i = digitalio.DigitalInOut(pin_motor_izquierda)
motor_i.direction = digitalio.Direction.OUTPUT

# Establecer el pin en alto
motor_i.value = True

luz = digitalio.DigitalInOut(pin_ledblanco)
luz.direction = digitalio.Direction.OUTPUT
luz = True

# Establecer el pin en alto
motor_d.value = True

# def enviar_texto(texto):
#     uart.write(texto.encode('utf-8')) 

from adafruit_ov7670 import (  # pylint: disable=unused-import
    OV7670,
    OV7670_SIZE_DIV16,
    OV7670_COLOR_YUV,
    OV7670_TEST_PATTERN_COLOR_BAR_FADE,
)


cam_bus = busio.I2C(board.GP19, board.GP18)

cam = OV7670(
    cam_bus,
    data_pins=[
        board.GP0,
        board.GP1,
        board.GP2,
        board.GP3,
        board.GP4,
        board.GP5,
        board.GP6,
        board.GP7,
    ],
    clock=board.GP9,
    vsync=board.GP13,
    href=board.GP12,
    mclk=board.GP8,
    shutdown=board.GP15,
    reset=board.GP14,
)

cam.size = OV7670_SIZE_DIV16
cam.colorspace = OV7670_COLOR_YUV
cam.flip_y = False






buf = bytearray(2 * cam.width * cam.height)

width = cam.width
row = bytearray(2 * width)



while True:
    
    cam.capture(buf)
    
    matrix = []
    rw = []
    for i in range(cam.width):
        intensity = "0" if buf[2 * (width * (cam.height-1) + i)] * 10 // 255 < 5 else "-"
        rw.append(intensity)
        
    matrix.append(rw)

    ulinea=matrix[len(matrix)-1][:]
    print(len(ulinea))
    suma=0
    contador=0
    for i in range(len(ulinea)):
        suma += i if ulinea[i]=="0" else 0
        contador += 1 if ulinea[i]=="0" else 0
    promedio=suma/contador if contador!=0 else 0
    
    diferencia=(20-promedio)*(100/20) if promedio!=0 else 100
    if promedio != 0 :
        if diferencia<0:
            print(abs(diferencia/100))
            pwm_derecha.duty_cycle = int(((vel_ini_derecha/100)*65535) * (1-abs((diferencia)/100)*0.8))
            pwm_izquierda.duty_cycle = int((vel_ini_izquierda/100)*65535)
        else:
            pwm_izquierda.duty_cycle = int(((vel_ini_izquierda/100)*65535) * (1-abs((diferencia)/100)*0.8)) 
            pwm_derecha.duty_cycle = int((vel_ini_derecha/100)*65535)
    else:
        pwm_derecha.duty_cycle = 0
        pwm_izquierda.duty_cycle = 0

    
    
    time.sleep(0.08)

    pwm_derecha.duty_cycle = 1000
    pwm_izquierda.duty_cycle = 1000
    
    
    




 