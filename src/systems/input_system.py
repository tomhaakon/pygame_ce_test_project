# src/systems/input_system.@property
import pygame

from ..ecs import Input, PlayerControlled


def input_system(world):
    """Leser keyboard og skriver til input komponenten fra PlayerControlled entites"""

    keys = pygame.key.get_pressed()

    move_x = 0.0
    move_y = 0.0

    if keys[pygame.K_w] or keys[pygame.K_UP]:
        move_y = -1.0
    if keys[pygame.K_s] or keys[pygame.K_DOWN]:
        move_y = 1.0
    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        move_x = -1.0
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        move_x = 1.0

    for _entity_id, input_component, _ in world.get_components(Input, PlayerControlled):
        input_component.move_x = move_x
        input_component.move_y = move_y
