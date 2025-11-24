# src/ecs.py
from dataclasses import dataclass


# -- components


@dataclass
class Position:
    x: float
    y: float


@dataclass
class Velocity:
    vx: float
    vy: float


@dataclass
class Renderable:
    width: int
    height: int
    color: tuple[int, int, int]


@dataclass
class PlayerControlled:
    """This is a tag that is saying this entity should only respond to player input"""

    pass


# Input komponenten lagrer resultatet av input
# "hvilken direction vil denne entitien bevege seg i denne framen
@dataclass
class Input:
    move_x: float = 0.0
    move_y: float = 0.0
    # senere:
    # jump: bool
    # attack: bool
    # interact: bool
    # aim_x: bool
    # aim_y: bool
    # eller actions: dict[str, bool]


@dataclass
class Player:
    id: int


# -- world / ecs core


class World:
    def __init__(self) -> None:
        self._next_entity_id: int = 0
        self._components: dict[type, dict[int, object]] = {}

    # -- entities
    def create_entity(self) -> int:
        entity_id = self._next_entity_id
        self._next_entity_id += 1
        return entity_id

    def add_component(self, entity: int, component: object) -> None:
        comp_type = type(component)
        if comp_type not in self._components:
            self._components[comp_type] = {}
        self._components[comp_type][entity] = component

    def get_component(self, entity: int, comp_type: type):
        return self._components.get(comp_type, {}).get(entity)

    def get_components(self, *component_types: type):

        if not component_types:
            return

        component_maps = []

        for component_type in component_types:
            component_dict = self._components.get(component_type)
            if not component_dict:
                return
            component_maps.append(component_dict)

        common_entity_ids = set(component_maps[0].keys())
        for component_dict in component_maps[1:]:
            common_entity_ids &= set(component_dict.keys())

        for entity_id in common_entity_ids:
            components = tuple(
                component_dict[entity_id] for component_dict in component_maps
            )
            yield (entity_id, *components)

    def destroy_entity(self, entity: int) -> None:
        for comp_dict in self._components.values():
            comp_dict.pop(entity, None)
