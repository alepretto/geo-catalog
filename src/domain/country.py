from dataclasses import dataclass


@dataclass(slots=True)
class Country:
    m49: int
    iso2: str | None
    iso3: str | None

    name: str

    region: str | None
    sub_region: str | None
    intermediate_region: str | None
