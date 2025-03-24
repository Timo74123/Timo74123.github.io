let bluetoothDevice;
let txCharacteristic;

async function connectBluetooth() {
    try {
        bluetoothDevice = await navigator.bluetooth.requestDevice({
            filters: [{ services: ['6e400001-b5a3-f393-e0a9-e50e24dcca9e'] }]
        });

        const server = await bluetoothDevice.gatt.connect();
        const service = await server.getPrimaryService('6e400001-b5a3-f393-e0a9-e50e24dcca9e');
        txCharacteristic = await service.getCharacteristic('6e400002-b5a3-f393-e0a9-e50e24dcca9e');

        console.log("Connecté au Raspberry Pi Pico W !");
        document.getElementById("status").innerText = "Connecté au Pico W";
    } catch (error) {
        console.error("Erreur de connexion :", error);
    }
}

async function sendCommand(command) {
    if (!txCharacteristic) {
        console.error("Bluetooth non connecté !");
        return;
    }
    const encoder = new TextEncoder();
    await txCharacteristic.writeValue(encoder.encode(command));
    console.log(`Commande envoyée : ${command}`);
}

// Associe les boutons aux commandes
document.getElementById("connect").addEventListener("click", connectBluetooth);
document.getElementById("player1").addEventListener("click", () => sendCommand("player1"));
document.getElementById("player2").addEventListener("click", () => sendCommand("player2"));
