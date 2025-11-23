# src/systems/input_system.@property
import pygame

from ..ecs import Input, PlayerControlled, Player


def input_system(world):
    """Leser keyboard og skriver til input komponenten fra PlayerControlled entites"""

    keys = pygame.key.get_pressed()

    for _entity_id, input_component, _pc, player in world.get_components(
        Input, PlayerControlled, Player
    ):

        move_x = 0.0
        move_y = 0.0

        if player.id == 1:
            # Player 1: WASD
            if keys[pygame.K_w]:
                move_y = -1.0
            if keys[pygame.K_s]:
                move_y = 1.0
            if keys[pygame.K_a]:
                move_x = -1.0
            if keys[pygame.K_d]:
                move_x = 1.0

        elif player.id == 2:
            # Player 2: Arrows
            if keys[pygame.K_UP]:
                move_y = -1.0
            if keys[pygame.K_DOWN]:
                move_y = 1.0
            if keys[pygame.K_LEFT]:
                move_x = -1.0
            if keys[pygame.K_RIGHT]:
                move_x = 1.0

        input_component.move_x = move_x
        input_component.move_y = move_y
