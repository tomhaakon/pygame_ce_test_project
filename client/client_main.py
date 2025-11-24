# client/cleint_main.py

import sys
import json
import socket

import pygame

from shared.ecs import World, Position, Renderable
from shared.player import create_player

HOST = "127.0.0.1"
PORT = 5000


class Game:
    def __init__(self):
        pygame.init()

        self.width = 800
        self.height = 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Client")

        self.clock = pygame.time.Clock()
        self.running = False

        # local ECS world used only for rendering
        self.world = World()
        self.player_entity = create_player(
            self.world, self.width / 2, self.height / 2, player_id=1
        )

        # Networking
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f"Client: connection to {HOST}:{PORT}...")
        self.sock.connect((HOST, PORT))
        self.sock.setblocking(False)

        self.recv_buffer = b""

    def run(self):
        self.running = True
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()

        sys.exit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self, dt: float):
        # 1 Read local keyboard - movement intent
        keys = pygame.key.get_pressed()
        move_x = 0.0
        move_y = 0.0

        if keys[pygame.K_w]:
            move_y = -1.0
        if keys[pygame.K_s]:
            move_y = 1.0
        if keys[pygame.K_a]:
            move_x = -1.0
        if keys[pygame.K_d]:
            move_x = 1.0

        if keys[pygame.K_ESCAPE]:
            self.running = False

        # 2. Send input to server
        input_msg = {
            "type": "input",
            "move_x": move_x,
            "move_y": move_y,
        }

        try:
            self.sock.sendall((json.dumps(input_msg) + "\n").encode("utf-8"))

        except (BrokenPipeError, ConnectionResetError):
            print("Client: lost connection to server")
            self.running = False
            return

        # 3. revice state updates from servre and apply to loccal ECS

        try:

            data = self.sock.recv(4006)
            if data:
                self.recv_buffer += data
                # process any complete lines
                while b"\n" in self.recv_buffer:
                    line, self.recv_buffer = self.recv_buffer.split(b"\n", 1)
                    if not line:
                        continue
                    msg = json.loads(line.decode("utf-8"))
                    if msg.get("type") == "state":
                        x = float(msg["x"])
                        y = float(msg["y"])
                        pos = self.world.get_component(self.player_entity, Position)
                        if pos is not None:
                            pos.x = x
                            pos.y = y
        except BlockingIOError:
            # no data this frame move on
            pass

    def draw(self):
        self.screen.fill((30, 30, 30))

        for _, pos, rend in self.world.get_components(Position, Renderable):
            rect = pygame.Rect(int(pos.x), int(pos.y), rend.width, rend.height)
            pygame.draw.rect(self.screen, rend.color, rect)

        pygame.display.flip()

    def quit(self):
        print("Client: quitting")
        try:
            self.slock.close()
        except Exception:
            pass

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    Game().run()
