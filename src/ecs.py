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

    
    def get_components(self, *comp_types: type):

        if not comp_types:
            return

        comp_dicts = []
        for t in comp_types:
            d = self._components.get(t)
            if not d:
                return
            comp_dicts.append(d)


        common_ids = set(comp_dicts[0].keys())
        for d in comp_dicts[1:]:
            common_ids &= set(d.keys())

        for entity_id in common_ids:
            yield (entity_id, *(d[entity_id] for d in comp_dicts))


