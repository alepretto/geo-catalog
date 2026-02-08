from dataclasses import dataclass


@dataclass(slots=True)
class District:
    id_district: int
    name: str
    id_city: int
