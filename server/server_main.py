# server/server_main.py

import time
import json
import socket
import threading

from shared.ecs import World, Position, Input, WorldConfig
from shared.player import create_player
from shared.systems.movement_system import movement_system

HOST = "127.0.0.1"
PORT = 5000

TICK_RATE = 60
DT = 1.0 / TICK_RATE

SERVER_RUNNING = True


def console_listener():
    global SERVER_RUNNING
    while SERVER_RUNNING:
        cmd = input("[server]:").strip().lower()
        if cmd in ("quit", "exit", "stop", "shutdown"):
            print("Server: shutdown command received.")
            SERVER_RUNNING = False
            break
        if cmd in ("help"):
            print("to shutdown server use 'quit, exit, stop or shutdown'")


def main():
    global SERVER_RUNNING

    world = World()
    world.set_resource(WorldConfig(width=500.0, height=500.0, tile_size=32))
    # Each client: { "conn", "addr", "player_id", "entity", "buffer" }
    clients: list[dict] = []
    next_player_id = 1

    print("Server: world initialized!")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind((HOST, PORT))
        server_sock.listen()
        server_sock.setblocking(False)  # non-blocking accept
        print(f"Server: listening on {HOST}:{PORT}")
        print("type help for info")

        threading.Thread(target=console_listener, daemon=True).start()

        while SERVER_RUNNING:
            frame_start = time.time()

            # --- 1. Accept new clients (non-blocking) ---
            try:
                conn, addr = server_sock.accept()
            except BlockingIOError:
                conn = None

            if conn is not None:
                conn.setblocking(False)
                player_id = next_player_id
                next_player_id += 1

                cfg = world.get_resource(WorldConfig)
                tile_size = cfg.tile_size if cfg is not None else 32

                tile_x, tile_y = 10, 15
                spawn_x = tile_x * tile_size
                spawn_y = tile_y * tile_size

                color = (0, 200, 0) if player_id == 1 else (200, 0, 0)

                entity = create_player(
                    world, spawn_x, spawn_y, player_id=player_id, color=color
                )

                client_info = {
                    "conn": conn,
                    "addr": addr,
                    "player_id": player_id,
                    "entity": entity,
                    "buffer": b"",
                }

                clients.append(client_info)

                print(f"Server: client {player_id} connected from {addr}")

                # send welcome message with player_id
                welcome_msg = {
                    "type": "welcome",
                    "player_id": player_id,
                    "world_width": cfg.width if cfg else None,
                    "world_height": cfg.height if cfg else None,
                }
                try:
                    conn.sendall((json.dumps(welcome_msg) + "\n").encode("utf-8"))
                except OSError:
                    print(f"Server: failed to send welcome to {addr}")

            # --- 2. Receive input from each client ---
            disconnected_clients: list[dict] = []

            for client in clients:
                conn = client["conn"]
                entity = client["entity"]

                try:
                    data = conn.recv(4096)
                    if not data:
                        print(
                            f"Server: client {client['player_id']} disconnected (empty recv)"
                        )
                        disconnected_clients.append(client)
                        continue

                    client["buffer"] += data

                    while b"\n" in client["buffer"]:
                        line, client["buffer"] = client["buffer"].split(b"\n", 1)
                        if not line:
                            continue
                        msg = json.loads(line.decode("utf-8"))
                        msg_type = msg.get("type")

                        if msg.get("type") == "input":
                            move_x = float(msg.get("move_x", 0.0))
                            move_y = float(msg.get("move_y", 0.0))

                            input_comp = world.get_component(entity, Input)
                            if input_comp is not None:
                                input_comp.move_x = move_x
                                input_comp.move_y = move_y

                        elif msg_type == "chat":
                            text = str(msg.get("text", "")).strip()
                            if text:
                                sender_id = client["player_id"]
                                chat_msg = {
                                    "type": "chat",
                                    "from": sender_id,
                                    "text": text,
                                }
                                chat_bytes = (json.dumps(chat_msg) + "\n").encode(
                                    "utf-8"
                                )

                                for other in clients:
                                    try:
                                        other["conn"].sendall(chat_bytes)

                                    except (
                                        ConnectionResetError,
                                        BrokenPipeError,
                                        ConnectionAbortedError,
                                        OSError,
                                    ):
                                        disconnected_clients.append(other)

                except BlockingIOError:
                    # no data this frame for this client
                    pass
                except (
                    ConnectionResetError,
                    ConnectionAbortedError,
                    BrokenPipeError,
                    OSError,
                ):
                    print(
                        f"Server: client {client['player_id']} disconnected (exception)"
                    )
                    disconnected_clients.append(client)

            # --- 3. Remove disconnected clients ---
            for client in disconnected_clients:
                try:
                    client["conn"].close()
                except OSError:
                    pass
                if client in clients:
                    clients.remove(client)

            if not SERVER_RUNNING:
                break

            # --- 4. Run ECS tick ---
            movement_system(world, DT)

            # --- 5. Build state of all players ---
            players_state = []
            for client in clients:
                entity = client["entity"]
                player_id = client["player_id"]
                pos = world.get_component(entity, Position)
                if pos is not None:
                    players_state.append({"id": player_id, "x": pos.x, "y": pos.y})

            state_msg = {"type": "state", "players": players_state}
            state_bytes = (json.dumps(state_msg) + "\n").encode("utf-8")

            # --- 6. Send state to all clients ---
            disconnected_clients = []
            for client in clients:
                try:
                    client["conn"].sendall(state_bytes)
                except (
                    ConnectionResetError,
                    BrokenPipeError,
                    ConnectionAbortedError,
                    OSError,
                ):
                    print(
                        f"Server: client {client['player_id']} disconnected while sending state"
                    )
                    disconnected_clients.append(client)

            for client in disconnected_clients:
                try:
                    client["conn"].close()
                except OSError:
                    pass
                if client in clients:
                    clients.remove(client)

            # --- 7. Sleep to maintain tickrate ---
            elapsed = time.time() - frame_start
            sleep_time = DT - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)

    print("Server: shutting down")


if __name__ == "__main__":
    main()
