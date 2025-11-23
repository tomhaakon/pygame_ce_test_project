# src\game.py
import sys

import pygame

from .ecs import Position, Renderable, World
from .player import create_player
from .systems.input_system import input_system
from .systems.movement_system import movement_system


class Game:
    def __init__(self) -> None:

        pygame.init()

        self.width: int = 800
        self.height: int = 600

        self.screen: pygame.Surface = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("pygame-ce testing")

        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.running: bool = False

        self.world = World()

        # player entity testing
        self.player1 = create_player(
            self.world, self.width / 3, self.height / 2, player_id=1, color=(0, 200, 0)
        )

        self.player2 = create_player(
            self.world,
            2 * self.width / 3,
            self.height / 2,
            player_id=2,
            color=(200, 0, 0),
        )

    def run(self):
        self.running = True
        while self.running:

            # fps 60
            delta_time: int = self.clock.tick(60) / 1000

            self.handle_events()
            self.update(delta_time)
            self.draw()

        self.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

        keys = pygame.key.get_pressed()

        if keys[pygame.K_ESCAPE]:
            self.running = False

    """
    --------------------------

    ### - Updateloop

    --------------------------
    """

    def update(self, delta_time: float):

        input_system(self.world)
        movement_system(self.world, delta_time)

    """
    --------------------------

    ### - Render

    --------------------------
    """

    def draw(self):

        self.screen.fill((30, 30, 30))

        for entity_id, position, render in self.world.get_components(
            Position, Renderable
        ):
            rect = pygame.Rect(
                int(position.x), int(position.y), render.width, render.height
            )
            pygame.draw.rect(self.screen, render.color, rect)

        pygame.display.flip()

    def quit(self):
        print("quit")
        pygame.quit()
        sys.exit()
