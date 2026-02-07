from dataclasses import dataclass


@dataclass(slots=True)
class District:
    id_distric: int
    name: str
    id_city: int
