# src/systems/movement_system.@property

from ..ecs import Position, Velocity, Input


def movement_system(world, dt):
    speed = 200.0

    for _entity_id, position, velocity, input_component in world.get_components(
        Position, Velocity, Input
    ):
        velocity.vx = input_component.move_x * speed
        velocity.vy = input_component.move_y * speed

        position.x += velocity.vx * dt
        position.y += velocity.vy * dt
