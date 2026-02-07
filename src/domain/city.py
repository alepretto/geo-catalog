from dataclasses import dataclass


@dataclass(slots=True)
class City:
    id_city: int
    name: str
    intermediate_region: str
    id_state: int
