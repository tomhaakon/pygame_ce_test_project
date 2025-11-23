# src\game.py
import sys

import pygame

from .ecs import Position, Renderable, Velocity, World
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
            dt: int = self.clock.tick(60) / 1000

            self.handle_events()
            self.update(dt)
            self.draw()

        self.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self, dt: float):

        keys = pygame.key.get_pressed()
        speed = 200

        vx = 0
        vy = 0

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            vy = -speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            vy = speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            vx = -speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            vx = speed

        if keys[pygame.K_ESCAPE]:
            self.running = False

        vel = self.world.get_component(self.player, Velocity)
        if vel is not None:
            vel.vx = vx
            vel.vy = vy

        for _, pos, vel in self.world.get_components(Position, Velocity):
            pos.x += vel.vx * dt
            pos.y += vel.vy * dt

    def draw(self):

        self.screen.fill((30, 30, 30))

        for _, pos, render in self.world.get_components(Position, Renderable):
            rect = pygame.Rect(int(pos.x), int(pos.y), render.width, render.height)
            pygame.draw.rect(self.screen, render.color, rect)

        pygame.display.flip()

    def quit(self):
        print("quit")
        pygame.quit()
        sys.exit()
