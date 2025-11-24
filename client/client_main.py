# client/client_main.py

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

        # mapping from player_id -> entity_id in this client's world
        self.player_entities: dict[int, int] = {}

        # Networking
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f"Client: connecting to {HOST}:{PORT}...")
        self.sock.connect((HOST, PORT))
        self.sock.setblocking(False)
        print("Client: connected!")

        self.recv_buffer = b""
        self.player_id: int | None = None

    def run(self):
        self.running = True
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()

        self.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self, dt: float):
        # 1. Read local keyboard movement intent
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
        except (BrokenPipeError, ConnectionResetError, OSError):
            print("Client: lost connection to server")
            self.running = False
            return

        # 3. Receive state updates from server and apply to local ECS
        try:
            data = self.sock.recv(4096)
            if data:
                self.recv_buffer += data

                # process any complete lines
                while b"\n" in self.recv_buffer:
                    line, self.recv_buffer = self.recv_buffer.split(b"\n", 1)
                    if not line:
                        continue
                    msg = json.loads(line.decode("utf-8"))
                    self.handle_message(msg)

        except BlockingIOError:
            # no data this frame
            pass
        except (BrokenPipeError, ConnectionResetError, OSError):
            print("Client: server disconnected")
            self.running = False
            return

    def handle_message(self, msg: dict):
        msg_type = msg.get("type")

        if msg_type == "welcome":
            # server assigns us a player_id
            self.player_id = int(msg["player_id"])
            print(f"Client: my player_id = {self.player_id}")

        elif msg_type == "state":
            players = msg.get("players", [])

            seen_ids: set[int] = set()

            for p in players:
                pid = int(p["id"])
                x = float(p["x"])
                y = float(p["y"])

                seen_ids.add(pid)

                # if we don't know this player yet, create local entity
                if pid not in self.player_entities:
                    if self.player_id is not None and pid == self.player_id:
                        color = (0, 200, 0)  # me = green
                    else:
                        color = (200, 0, 0)  # others = red

                    entity = create_player(self.world, x, y, player_id=pid, color=color)
                    self.player_entities[pid] = entity

                entity = self.player_entities[pid]
                pos = self.world.get_component(entity, Position)
                if pos is not None:
                    pos.x = x
                    pos.y = y

            # despawn players that no longer is connected
            for pid in list(self.player_entities.keys()):
                if pid not in seen_ids:
                    entity = self.player_entities[pid]
                    self.world.destroy_entity(entity)
                    del self.player_entities[pid]

    def draw(self):
        self.screen.fill((30, 30, 30))

        for _, pos, rend in self.world.get_components(Position, Renderable):
            rect = pygame.Rect(int(pos.x), int(pos.y), rend.width, rend.height)
            pygame.draw.rect(self.screen, rend.color, rect)

        pygame.display.flip()

    def quit(self):
        print("Client: quitting")
        try:
            self.sock.close()
        except Exception:
            pass
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    Game().run()
