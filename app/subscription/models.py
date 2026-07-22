from dataclasses import dataclass, field


@dataclass
class Endpoint:
    country: str
    protocol: str
    address: str
    port: int
    config: dict

@dataclass
class Country:
    name: str
    endpoints: list["Endpoint"] = field(default_factory=list)
    selected_endpoint: Endpoint | None = None