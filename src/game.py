# src\game.py
import sys

import pygame

from .ecs import Position, Renderable, Velocity, World, PlayerControlled
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

        velocity_x = 0
        velocity_y = 0

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            velocity_y = -speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            velocity_y = speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            velocity_x = -speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            velocity_x = speed

        if keys[pygame.K_ESCAPE]:
            self.running = False

        # input system
        # applies to any entity with velocity + PlayerControlled
        # for entityid, velocity, playercontrolled
        for entity_id, velocity, player_controlled in self.world.get_components(
            Velocity, PlayerControlled
        ):
            velocity.vx = velocity_x
            velocity.vy = velocity_y

        # movementsystem
        for entity_id, position, velocity in self.world.get_components(
            Position, Velocity
        ):
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
