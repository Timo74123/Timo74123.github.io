let bluetoothDevice;
let ledService;
let player1Char, player2Char;

document.getElementById("connect").addEventListener("click", async () => {
    try {
        bluetoothDevice = await navigator.bluetooth.requestDevice({
            acceptAllDevices: true,
            optionalServices: ['12345678-1234-5678-1234-56789abcdef0'] // UUID du service BLE
        });

        const server = await bluetoothDevice.gatt.connect();
        ledService = await server.getPrimaryService('12345678-1234-5678-1234-56789abcdef0');

        player1Char = await ledService.getCharacteristic('abcdef01-1234-5678-1234-56789abcdef0');
        player2Char = await ledService.getCharacteristic('abcdef02-1234-5678-1234-56789abcdef0');

        console.log("Connecté au Raspberry Pi Pico W !");
    } catch (error) {
        console.error("Erreur de connexion :", error);
    }
});

document.getElementById("player1").addEventListener("click", async () => {
    if (player1Char) {
        await player1Char.writeValue(new Uint8Array([1]));
    }
});

document.getElementById("player2").addEventListener("click", async () => {
    if (player2Char) {
        await player2Char.writeValue(new Uint8Array([1]));
    }
});
