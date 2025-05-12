"""
Description: Commande d'un bandeau lumineux de type WS2812 depuis un Raspberry Pi Pico.
Le signal envoyé au bandeau est configuré par défaut sur le GPIO0 du Pico.
"""
from bt_controller.module import BtController 
from led_controller import LedController


class BtControllerLed(BtController):
    WINNING_CLICKS = 120  # Nombre de clics pour gagner (1 clic = 1 LED)

    def __init__(self, led_controller, name=None):
        super().__init__(name)
        self._led_controller = led_controller
        self._player_clicks = [0, 0]
        self._player_positions = [0, 0]
        self._player_colors = [LedController.RED, LedController.BLUE]
        self._game_over = False

        self._led_controller.set_led_color(LedController.BLACK)
        self._led_controller.update_pixel()

    def on_rx(self, data):
        data = data.decode('utf-8').strip()
        print(f"data utf-8={data}")

        if data == "reset":
            self._reset_game()
            return

        if self._game_over:
            print("Partie terminée. Ignorer les clics.")
            return

        if data == "player1":
            self._handle_click(0)
        elif data == "player2":
            self._handle_click(1)

    def _handle_click(self, player_index):
        self._player_clicks[player_index] += 1
        print(f"Joueur {player_index + 1} a {self._player_clicks[player_index]} clics.")

        if self._player_clicks[player_index] >= self.WINNING_CLICKS:
            print(f"Joueur {player_index + 1} a atteint {self._player_clicks[player_index]} clics -> GAGNÉ")
            self._send_winner(player_index)
            self._game_over = True

        self._advance_led(player_index)

    def _advance_led(self, player_index):
        current_position = self._player_positions[player_index]
        new_position = current_position + 1

        if new_position >= self._led_controller.num_leds:
            print(f"Joueur {player_index + 1} a atteint la fin du bandeau.")
            return  # ne pas dépasser les LED disponibles

        other_index = 1 - player_index
        other_position = self._player_positions[other_index]

        # Effacer la LED précédente
        if current_position == other_position:
            self._led_controller.pixel_array[current_position] = self._get_current_color(other_index)
        else:
            self._led_controller.pixel_array[current_position] = 0

        # Allumer la nouvelle LED
        if new_position == other_position:
            mixed_color = self._mix_colors(self._player_colors[player_index], self._player_colors[other_index])
            self._led_controller.pixel_array[new_position] = mixed_color
        else:
            self._led_controller.pixel_array[new_position] = self._get_current_color(player_index)

        self._player_positions[player_index] = new_position
        self._led_controller.update_pixel()

    def _reset_game(self):
        print("Jeu réinitialisé.")
        self._player_clicks = [0, 0]
        self._player_positions = [0, 0]
        self._game_over = False
        self._led_controller.set_led_color(LedController.BLACK)
        self._led_controller.update_pixel()

    def _get_current_color(self, player_index):
        color = self._player_colors[player_index]
        return (color[1] << 16) + (color[0] << 8) + color[2]

    def _mix_colors(self, color1, color2):
        r = (color1[0] + color2[0]) // 2
        g = (color1[1] + color2[1]) // 2
        b = (color1[2] + color2[2]) // 2
        return (g << 16) + (r << 8) + b

    def _send_winner(self, player_index):
        try:
            message = f"GAGNANT: Player {player_index + 1}"
            print("Envoi Bluetooth:", message)
            if hasattr(self, 'tx') and self.tx:
                self.tx.write(message.encode())
            else:
                print("TX non disponible")
        except Exception as e:
            print("Erreur d'envoi gagnant:", e)


if __name__ == "__main__":
    led_controller = LedController(num_leds=120)  # Assurez-vous que le bandeau a bien 120 LEDs
    btController = BtControllerLed(led_controller, "TH")
    btController.start()

