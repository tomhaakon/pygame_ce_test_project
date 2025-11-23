# src\game.py
import sys

import pygame

from .ecs import Position, Renderable, Velocity, World, PlayerControlled, Input
from .player import create_player


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
        self.player = create_player(self.world, self.width / 2, self.height / 2)

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

    def update(self, delta_time: float):

        keys = pygame.key.get_pressed()
        speed = 200

        move_x = 0
        move_y = 0

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            move_y = -1.0
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            move_y = 1.0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            move_x = -1.0
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            move_x = 1.0

        if keys[pygame.K_ESCAPE]:
            self.running = False

        # --------------------------
        #
        # input system
        #
        # --------------------------

        for (
            _entity_id,
            input_component,
            _player_controlled,
        ) in self.world.get_components(Input, PlayerControlled):
            input_component.move_x = move_x
            input_component.move_y = move_y

        # --------------------------
        #
        # movement system
        #
        # --------------------------
        for (
            _entity_id,
            position,
            velocity,
            input_component,
        ) in self.world.get_components(Position, Velocity, Input):

            # konverter input (-1..1) til ekte velocity i pixel/per sek
            velocity.vx = input_component.move_x * speed
            velocity.vy = input_component.move_y * speed

            # tilfør velocity til posisjon med delta time
            position.x += velocity.vx * delta_time
            position.y += velocity.vy * delta_time

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
