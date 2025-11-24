# server/server_main.py

import time
import json
import socket
import threading

from shared.ecs import World, Position, Input
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
        cmd = input("").strip().lower()
        if cmd in ("quit", "exit", "stop", "shutdown"):
            print("Server: shutdown command received.")
            SERVER_RUNNING = False
            break


def main():
    global SERVER_RUNNING

    world = World()

    player_entity = create_player(world, 400, 300, player_id=1)

    threading.Thread(target=console_listener, daemon=True).start()

    print("Server: world initalized!")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind((HOST, PORT))
        server_sock.listen(1)
        server_sock.settimeout(1.0)
        print(f"Server: listening on {HOST}:{PORT}")

        print("Server: waiting for a client...")

        while SERVER_RUNNING:  # outer loop: accept new clients

            try:
                conn, addr = server_sock.accept()

            except socket.timeout:
                # check shutdown flag occasionally
                continue

            print(f"Server: cleint connected from {addr}")

            with conn:
                conn.settimeout(1.0)
                running = True
                recv_buffer = b""

                while running and SERVER_RUNNING:
                    frame_start = time.time()

                    # ----1. Recieve any input messages from client ---

                    try:
                        data = conn.recv(4096)
                        if not data:
                            print("Server: client disonnected (empty recv)")
                            break

                        recv_buffer += data

                        # process all complete lines (newline-delimited JSON)
                        while b"\n" in recv_buffer:
                            line, recv_buffer = recv_buffer.split(b"\n", 1)
                            if not line:
                                continue
                            msg = json.loads(line.decode("utf-8"))
                            if msg.get("type") == "input":
                                move_x = float(msg.get("move_x", 0.0))
                                move_y = float(msg.get("move_y", 0.0))

                                input_comp = world.get_component(player_entity, Input)
                                if input_comp is not None:
                                    input_comp.move_x = move_x
                                    input_comp.move_y = move_y

                    except socket.timeout:
                        pass

                    except (
                        ConnectionResetError,
                        ConnectionAbortedError,
                        BrokenPipeError,
                    ):
                        print("Server: client disconnected (exception)")
                        break
                    if not SERVER_RUNNING:
                        break

                    # --- 2 Run ECS Tick on the server ---
                    movement_system(world, DT)

                    # --- 3 Send back the players positino
                    pos = world.get_component(player_entity, Position)
                    if pos is not None:
                        state_msg = {
                            "type": "state",
                            "x": pos.x,
                            "y": pos.y,
                        }
                        try:
                            conn.sendall((json.dumps(state_msg) + "\n").encode("utf-8"))
                        except (ConnectionResetError, BrokenPipeError):
                            print("Server: client disonnection while sending state")
                            break

                    # --- 4 Sleep to maintain tick rate --

                    elapsed = time.time() - frame_start
                    sleep_time = DT - elapsed
                    if sleep_time > 0:
                        time.sleep(sleep_time)


if __name__ == "__main__":
    main()
