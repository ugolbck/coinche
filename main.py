from textual import on, work
from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Header, Footer, Button, Static
from textual.screen import Screen
import websockets


class WelcomeScreen(Screen):
    """The welcome screen with a Join Game button."""

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="welcome-container"):
            yield Button("Join Game", variant="primary", id="join")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "join":
            self.app.push_screen("game")

class GameScreen(Screen):
    """The main game screen showing cards and game state."""
    
    def compose(self) -> ComposeResult:
        yield Container(
            Static("", id="teammate", classes="player-name"),
            Static("", id="left-opponent", classes="player-name"),
            Static("", id="right-opponent", classes="player-name"),
            Static("", id="cards", classes="cards"),
            id="game-layout"
        )

    @work(exclusive=True)
    async def connect_to_game(self) -> None:
        """Connect to the game server and handle messages."""
        cards_display = self.query_one("#cards", Static)
        teammate_display = self.query_one("#teammate", Static)
        left_opponent_display = self.query_one("#left-opponent", Static)
        right_opponent_display = self.query_one("#right-opponent", Static)
        
        try:
            async with websockets.connect('ws://localhost:8000/ws') as websocket:                
                while True:
                    message = await websocket.recv()
                    if "cards:" in message:
                        cards = message.split(":")[1]
                        cards_display.update(cards)
                    elif "teammate:" in message:
                        teammate = message.split(":")[1]
                        teammate_display.update(teammate)
                    elif "left_opponent:" in message:
                        left_opponent = message.split(":")[1]
                        left_opponent_display.update(left_opponent)
                    elif "right_opponent:" in message:
                        right_opponent = message.split(":")[1]
                        right_opponent_display.update(right_opponent)
                    else:
                        # Handle other game messages
                        self.app.log(message)
                        
        except Exception as e:
            self.app.log(f"Connection error: {str(e)}")

    def on_mount(self) -> None:
        """When the screen is mounted, connect to the game server."""
        self.connect_to_game()

class CoincheTUIClient(App):
    """A Textual client for the Coinche game."""
    
    CSS = """
    #game-layout {
        layout: grid;
        grid-size: 3 3;
        grid-rows: 1fr 1fr 1fr;
        grid-columns: 1fr 1fr 1fr;
        padding: 1;
    }

    .player-name {
        content-align: center middle;
    }

    #teammate {
        column-span: 3;
        content-align: center middle;
        border: solid green;
    }

    #left-opponent {
        content-align: center middle;
        border: solid blue;
    }

    #right-opponent {
        content-align: center middle;
        border: solid blue;
    }

    #cards {
        column-span: 3;
        content-align: center middle;
        border: solid red;
    }

    Screen {
        align: center middle;
    }
    """

    SCREENS = {
        "welcome": WelcomeScreen,
        "game": GameScreen
    }

    BINDINGS = [
        ("q", "quit", "Quit"),
    ]

    def on_mount(self) -> None:
        """When the app starts, show the welcome screen."""
        self.push_screen("welcome")

if __name__ == "__main__":
    app = CoincheTUIClient()
    app.run()