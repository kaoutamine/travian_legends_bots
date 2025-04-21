from dataclasses import dataclass
from typing import Optional

@dataclass
class GameWorld:
    name: str
    url: str

@dataclass
class Avatar:
    uuid: str
    name: str
    world: GameWorld

@dataclass
class Coordinates:
    x: int
    y: int

@dataclass
class OasisInfo:
    coordinates: Coordinates
    type: str
    owner: Optional[str]
    troops: Optional[dict]
    resources: Optional[dict] 