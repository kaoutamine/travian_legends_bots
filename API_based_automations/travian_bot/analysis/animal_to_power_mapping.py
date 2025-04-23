# Average of (infantry + cavalry defense)
ANIMAL_POWER_MAP = {
    "rat": 17.5,
    "spider": 27.5,
    "snake": 50,
    "bat": 73,
    "wild boar": 60,
    "boar": 60,
    "wolf": 90,
    "bear": 195,
    "crocodile": 415,
    "tiger": 185,
    "elephant": 520
}

# Handles ambiguous or alternate names (e.g. from image alt tags or filenames)
ANIMAL_IDENTIFIER_MAP = {
    "rat": "rat",
    "spider": "spider",
    "snake": "snake",
    "bat": "bat",
    "boar": "wild boar",  # unify both keys
    "wild boar": "wild boar",
    "wolf": "wolf",
    "bear": "bear",
    "crocodile": "crocodile",
    "tiger": "tiger",
    "elephant": "elephant"
}

def get_animal_power(animal_name: str) -> float:
    """Get average defense-based power for a given animal name."""
    canonical_name = ANIMAL_IDENTIFIER_MAP.get(animal_name.lower().strip(), "rat")
    return ANIMAL_POWER_MAP.get(canonical_name, 1)
