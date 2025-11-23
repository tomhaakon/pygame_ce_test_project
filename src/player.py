#player.py
from .ecs import Position, Velocity, Renderable, World


def create_player(world: World, x: float, y: float) -> int:

    player = world.create_entity()

    world.add_component(player, Position(x, y))
    world.add_component(player, Velocity(0, 0))
    world.add_component(player, Renderable(32, 32, (0, 200, 0)))

    return player
