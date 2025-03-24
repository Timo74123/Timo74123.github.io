from machine import Pin
from time import sleep
import bluetooth
from micropython import const
from ble_simple_peripheral import BLESimplePeripheral

led_pins = [2, 3]  # GPIO pour les LEDs
leds = [Pin(pin, Pin.OUT) for pin in led_pins]
positions = [0, 0]  # Position des LEDs

ble = bluetooth.BLE()
p = BLESimplePeripheral(ble)

def update_leds():
    for i, led in enumerate(leds):
        led.value(1 if positions[i] % 2 == 0 else 0)  # Clignotement en fonction de la position

def on_rx(data):
    global positions
    if data == b'\x01':  # Commande du joueur 1
        positions[0] += 1
    elif data == b'\x02':  # Commande du joueur 2
        positions[1] += 1
    update_leds()

p.on_write(on_rx)

while True:
    sleep(0.1)
