
#https://github.com/pi3g/pico-w/tree/main/MicroPython/I%20Pico%20W%20LED%20web%20server
#https://youtu.be/Or-UVgiMQsU
from machine import Pin, PWM,Timer,ADC
import rp2
import network
import ubinascii
import machine
import urequests as requests
import time
#from secrets import secrets
import socket

import utime

#Configurando el p
# Define los pines para controlar los motores
input1_1 = Pin(16, Pin.OUT)
input1_2 = Pin(17, Pin.OUT)

input2_1 = Pin(18, Pin.OUT)
input2_2 = Pin(19, Pin.OUT)

# Define los pines PWM para controlar la velocidad de los motores
pwm_pin1 = Pin(20)  # Pin 18 para control de velocidad del motor 1
pwm1 = PWM(pwm_pin1)
pwm1.freq(1000)  # Frecuencia del PWM (Hz)

pwm_pin2 = Pin(21)  # Pin 19 para control de velocidad del motor 2
pwm2 = PWM(pwm_pin2)
pwm2.freq(1000)  # Frecuencia del PWM (Hz)

adc = ADC(0) #pin GP26
timer = Timer()

def control_motor(input1, input2, pwm, speed, direction):
    pwm.duty_u16(int(65535 * speed/100))  # Establece el ciclo de trabajo del PWM
    if direction == 1:
        input1.on()
        input2.off()
    elif direction == -1:
        input1.off()
        input2.on()
    else:
        input1.off()
        input2.off()
        
def forward(speed1, speed2):
    control_motor(input1_1, input1_2, pwm1, speed1, 1)  # Motor 1 hacia adelante con velocidad speed1
    control_motor(input2_1, input2_2, pwm2, speed2, 1)  # Motor 2 hacia adelante con velocidad speed2

def backward(speed1, speed2):
    control_motor(input1_1, input1_2, pwm1, speed1, -1)  # Motor 1 hacia atras con velocidad speed1
    control_motor(input2_1, input2_2, pwm2, speed2, -1)  # Motor 2 hacia atras con velocidad speed2
    
def left_har(speed1, speed2):
    control_motor(input1_1, input1_2, pwm1, speed1, 1)  # Motor 1 hacia adelante con velocidad speed1
    control_motor(input2_1, input2_2, pwm2, speed2, -1)  # Motor 2 hacia adelante con velocidad speed2

def rigth_har(speed1, speed2):
    control_motor(input1_1, input1_2, pwm1, speed1, -1)  # Motor 1 hacia adelante con velocidad speed1
    control_motor(input2_1, input2_2, pwm2, speed2, 1)  # Motor 2 hacia adelante con velocidad speed2

def lef(speed1, speed2):
    control_motor(input1_1, input1_2, pwm1, speed1, 1)  # Motor 1 hacia adelante con velocidad speed1
    control_motor(input2_1, input2_2, pwm2, speed2, 1)  # Motor 2 hacia adelante con velocidad speed2

def rigt(speed1, speed2):
    control_motor(input1_1, input1_2, pwm1, speed1, 1)  # Motor 1 hacia adelante con velocidad speed1
    control_motor(input2_1, input2_2, pwm2, speed2, 1)  # Motor 2 hacia adelante con velocidad speed2
        
    
def stop():
    control_motor(input1_1, input1_2, pwm1, 0, 0)
    control_motor(input2_1, input2_2, pwm2, 0, 0)

def blink(timer):
    adc_value=(adc.read_u16()/65535)*100
    adc_value= (adc_value-50)*2

timer.init(freq=3,mode=Timer.PERIODIC,callback=blink) #ejecuta la rutina blink Interrumpe 5 veces cada 2 segundos

# Set country to avoid possible errors
#rp2.country('DE')

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
# If you need to disable powersaving mode
# wlan.config(pm = 0xa11140)

# See the MAC address in the wireless chip OTP
mac = ubinascii.hexlify(network.WLAN().config('mac'),':').decode()
print('mac = ' + mac)

# Other things to query
# print(wlan.config('channel'))
# print(wlan.config('essid'))
# print(wlan.config('txpower'))

# Load login data from different file for safety reasons
ssid = "Pglo"
pw = "stks6105"
wlan.connect(ssid, pw)

# Wait for connection with 10 second timeout
timeout = 10
while timeout > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    timeout -= 1
    print('Waiting for connection...')
    time.sleep(1)

# Define blinking function for onboard LED to indicate error codes    
def blink_onboard_led(num_blinks):
    led = machine.Pin('LED', machine.Pin.OUT)
    for i in range(num_blinks):
        led.on()
        time.sleep(.2)
        led.off()
        time.sleep(.2)
    
# Handle connection error
# Error meanings
# 0  Link Down
# 1  Link Join
# 2  Link NoIp
# 3  Link Up
# -1 Link Fail
# -2 Link NoNet
# -3 Link BadAuth

wlan_status = wlan.status()
blink_onboard_led(wlan_status)

if wlan_status != 3:
    raise RuntimeError('Wi-Fi connection failed ',wlan_status)
else:
    print('Connected')
    status = wlan.ifconfig()
    print('ip = ' + status[0])
    
# Function to load in html page    
def get_html(html_name):
    with open(html_name, 'r') as file:
        html = file.read()
        
    return html


def get_adc_value():
    adc_value = (adc.read_u16() / 65535) * 100
    adc_value = (adc_value - 50) * 2
    return adc_value


# HTTP server with socket
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]


s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

s.bind(addr)

s.listen(1)

print('Listening on', addr)
led = machine.Pin('LED', machine.Pin.OUT)

# Listen for connections
while True:
    try:
        cl, addr = s.accept()
        print('Client connected from', addr)
        r = cl.recv(1024)
        
        r = str(r)
        motor_forward = r.find('?motor=forward')
        motor_backward = r.find('?motor=backward')
        motor_stop = r.find('?motor=stop')
        left_hard = r.find('?left=hard')
        rigth_hard = r.find('?rigth=hard')
        left = r.find('?left=left')
        rigth = r.find('?rigth=rigth')
        quite = r.find('quite=quite')
        
        if motor_forward > -1:
            print('Forward')
            forward(80, 80)  # Ejemplo de velocidad diferente para cada motor
            
        if motor_backward > -1:
            print('Backward')
            backward(80, 80)  # Ejemplo de velocidad diferente para cada motor
            
        if motor_stop > -1:
            print('Stop')
            stop()
        
        if left_hard >-1:
            left_har( 75,70)
            print('Left hard')
        
        if rigth_hard >-1:
            rigth_har( 75,70)
            print('rigth hard')
            
        if left >-1:
            lef( 70,55)
            print('Left')
        
        if rigth>-1:
            rigt( 55,70)
            print('rigth')

        if quite > -1:
            print('QUIT')
            cl.close()
            #print('Connection closed')
            s.close()
            wlan.active(False)
            wlan.disconnect()
            print('Bye')
            break
        
        # Read ADC value
        adc_value = get_adc_value()

        # Send HTML response with updated ADC value
        response = get_html('web_server_cube.html').replace('{adc_value}', str(adc_value))
        cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        cl.send(response)
        cl.close()
        
        # Print debug info
        print('ADC Value:', adc_value)
        
    except OSError as e:
        cl.close()
        print('Connection closed')

# Make GET request
#request = requests.get('http://www.google.com')
#print(request.content)
#request.close()


