#https://docs.circuitpython.org/projects/ov7670/en/latest/examples.html
# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2021 Jeff Epler for Adafruit Industries
#
# SPDX-License-Identifier: Unlicense

"""Capture an image from the camera and display it as ASCII art.

The camera is placed in YUV mode, so the top 8 bits of each color
value can be treated as "greyscale".

It's important that you use a terminal program that can interpret
"ANSI" escape sequences.  The demo uses them to "paint" each frame
on top of the prevous one, rather than scrolling.

Remember to take the lens cap off, or un-comment the line setting
the test pattern!
"""

import sys
import time
import pwmio
import digitalio
import busio
import board

vel_ini_derecha=100;
vel_ini_izquierda=100;
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

def enviar_texto(texto):
    uart.write(texto)

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






print(cam.width, cam.height)

buf = bytearray(2 * cam.width * cam.height)

width = cam.width
row = bytearray(2 * width)



while True:
    # Crear el texto con las velocidades de los motores
    led.value = True
    time.sleep(0.1)
    led.value = False
    time.sleep(1)  # Puedes ajustar el intervalo de envío según tus necesidades
    cam.capture(buf)
    matrix = []
    for j in range(cam.height):
        rw = []
        for i in range(cam.width):
            intensity = "0" if buf[2 * (width * j + i)] * 10 // 255 < 5 else "-"
            rw.append(intensity)        
            print(intensity, end=' ')
        matrix.append(rw)

    ulinea=matrix[len(matrix)-1][:]
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
            pwm_derecha.duty_cycle = int(((vel_ini_derecha/100)*65535) * (1-abs((diferencia)/100)))
            pwm_izquierda.duty_cycle = int((vel_ini_izquierda/100)*65535)
        else:
            pwm_izquierda.duty_cycle = int(((vel_ini_izquierda/100)*65535) * (1-abs((diferencia)/100))) 
            pwm_derecha.duty_cycle = int((vel_ini_derecha/100)*65535)
    else:
        pwm_derecha.duty_cycle = 0
        pwm_izquierda.duty_cycle = 0

#     
#     print(diferencia)
#     print(pwm_derecha.duty_cycle)
#     print(pwm_izquierda.duty_cycle)

    # Crear el texto con las velocidades de los motores
    texto_a_enviar = "Vel motor 1 = {}\nVel motor 2 = {}".format(pwm_derecha.duty_cycle, pwm_izquierda.duty_cycle)
    # Enviar el texto
    enviar_texto(texto_a_enviar)
    texto_a_enviar = ""
    # Enviar el texto
    enviar_texto(texto_a_enviar)
    time.sleep(0.01)  # Puedes ajustar el intervalo de envío según tus necesidades

    pwm_derecha.duty_cycle = 0
    pwm_izquierda.duty_cycle =0
    
    
    
    
    
