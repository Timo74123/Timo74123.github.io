"""
Description: périphérique bluetooth de type UART (Universal Asynchronous Receiver Transmitter)
pour la transmission et la réception de texte.
"""

import bluetooth
import time
from .ble_advertising import advertising_payload

from micropython import const


class BtController:
    def __init__(self, name="btc"):
        print("BtController instanciated")

        # const
        self._IRQ_CENTRAL_CONNECT = const(1)
        self._IRQ_CENTRAL_DISCONNECT = const(2)
        self._IRQ_GATTS_WRITE = const(3)

        self._FLAG_READ = const(0x0002)
        self._FLAG_WRITE_NO_RESPONSE = const(0x0004)
        self._FLAG_WRITE = const(0x0008)
        self._FLAG_NOTIFY = const(0x0010)

        self._UART_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
        self._UART_TX = (
            bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E"),
            self._FLAG_READ | self._FLAG_NOTIFY,
        )
        self._UART_RX = (
            bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E"),
            self._FLAG_WRITE | self._FLAG_WRITE_NO_RESPONSE,
        )
        self._UART_SERVICE = (
            self._UART_UUID,
            (self._UART_TX, self._UART_RX),
        )

        # Create a Bluetooth Low Energy (BLE) object
        self._ble = bluetooth.BLE()
        self._ble.active(True)
        self._ble.irq(self._irq)
        ((self._handle_tx, self._handle_rx),) = self._ble.gatts_register_services((self._UART_SERVICE,))
        self._connections = set()
        self._write_callback = None
        self._payload = advertising_payload(name=name, services=[self._UART_UUID])
        self._advertise()

    def _irq(self, event, data):
        # Track connections so we can send notifications.
        if event == self._IRQ_CENTRAL_CONNECT:
            conn_handle, _, _ = data
            print("New connection", conn_handle)
            self._connections.add(conn_handle)
        elif event == self._IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _ = data
            print("Disconnected", conn_handle)
            self._connections.remove(conn_handle)
            # Start advertising again to allow a new connection.
            self._advertise()
        elif event == self._IRQ_GATTS_WRITE:
            conn_handle, value_handle = data
            value = self._ble.gatts_read(value_handle)
            if value_handle == self._handle_rx and self._write_callback:
                self._write_callback(value)

    def send(self, data):
        for conn_handle in self._connections:
            self._ble.gatts_notify(conn_handle, self._handle_tx, data)

    def is_connected(self):
        return len(self._connections) > 0

    def _advertise(self, interval_us=500000):
        print("Starting advertising")
        self._ble.gap_advertise(interval_us, adv_data=self._payload)

    def on_write(self, callback):
        self._write_callback = callback

    def on_rx(self, data): # maximum 20 bytes per message
        print("Data received: ", data)  # Print the received data

    def start(self):
        while True:
            if self.is_connected():  # Check if a BLE connection is established
                self.on_write(self.on_rx)  # Set the callback function for data reception
        time.sleep_ms(100)


def demo():
    ble = bluetooth.BLE()
    p = BLESimplePeripheral(ble)

    def on_rx(v):
        print("RX", v)

    p.on_write(on_rx)

    i = 0
    while True:
        if p.is_connected():
            # Short burst of queued notifications.
            for _ in range(3):
                data = str(i) + "_"
                print("TX", data)
                p.send(data)
                i += 1
        time.sleep_ms(100)


if __name__ == "__main__":
    demo()


