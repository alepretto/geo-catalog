from dataclasses import dataclass


@dataclass(slots=True)
class State:
    id_state: int
    name: str
    short_name: str
    region: str
    region_short_name: str
