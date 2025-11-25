# player.py
from .ecs import (
    Position,
    Velocity,
    Renderable,
    World,
    PlayerControlled,
    Input,
    Player,
    Health,
)


def create_player(
    world: World, x: float, y: float, player_id: int, color=(0, 200, 0)
) -> int:

    player = world.create_entity()

    world.add_component(player, Position(x, y))
    world.add_component(player, Velocity(0, 0))
    world.add_component(player, Renderable(width=32, height=32, color=color))
    world.add_component(player, PlayerControlled())
    world.add_component(player, Input())
    world.add_component(player, Player(player_id))
    world.add_component(player, Health(current=100, maximum=100))

    return player
