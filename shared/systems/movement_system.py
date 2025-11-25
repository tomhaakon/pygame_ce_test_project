# src/systems/movement_system.@property

from ..ecs import Position, Velocity, Input, Renderable, WorldConfig


def movement_system(world, dt: float):
    speed = 200.0

    cfg = world.get_resource(WorldConfig)
    world_width = cfg.width if cfg is not None else None
    world_height = cfg.height if cfg is not None else None

    for _entity_id, position, velocity, input_component, render in world.get_components(
        Position, Velocity, Input, Renderable
    ):
        # 1. apply input -> velocity
        velocity.vx = input_component.move_x * speed
        velocity.vy = input_component.move_y * speed

        # 2. interaget position
        position.x += velocity.vx * dt
        position.y += velocity.vy * dt

        # 3. Clamp to world bounds
        if world_width is not None and world_height is not None:
            # left/top
            if position.x < 0:
                position.x = 0
            if position.y < 0:
                position.y = 0

            # right/bottom (subract rect size)
            if position.x + render.width > world_width:
                position.x = world_width - render.width
            if position.y + render.height > world_height:
                position.y = world_height - render.height
