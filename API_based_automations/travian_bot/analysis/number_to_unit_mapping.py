# unit_mappings.py

# Roman units
roman_units = {
    "u1": "Legionnaire",
    "u2": "Praetorian",
    "u3": "Imperian",
    "u4": "Equites Legati",
    "u5": "Equites Imperatoris",
    "u6": "Equites Caesaris",
    "u7": "Battering Ram",
    "u8": "Fire Catapult",
    "u9": "Senator",
    "u10": "Settler",
    "hero": "Hero"
}

# Gaul units
gaul_units = {
    "u1": "Phalanx",
    "u2": "Swordsman",
    "u3": "Pathfinder",
    "u4": "Theutates Thunder",
    "u5": "Druidrider",
    "u6": "Haeduan",
    "u7": "Trebuchet",
    "u8": "Ram",
    "u9": "Chieftain",
    "u10": "Settler",
    "hero": "Hero"
}

# Teuton units
teuton_units = {
    "u1": "Clubswinger",
    "u2": "Spearman",
    "u3": "Axeman",
    "u4": "Scout",
    "u5": "Paladin",
    "u6": "Teutonic Knight",
    "u7": "Ram",
    "u8": "Catapult",
    "u9": "Chief",
    "u10": "Settler",
    "hero": "Hero"
}

# Egyptian units
egyptian_units = {
    "u1": "Slave Militia",
    "u2": "Ash Warden",
    "u3": "Khopesh Warrior",
    "u4": "Anhur Guard",
    "u5": "Resheph Chariot",
    "u6": "Ram",
    "u7": "Stone Catapult",
    "u8": "Nomarch",
    "u9": "Settler",
    "u10": "Supply Wagon",
    "hero": "Hero"
}

# Hun units
hun_units = {
    "u1": "Mercenary",
    "u2": "Bowman",
    "u3": "Spotter",
    "u4": "Steppe Rider",
    "u5": "Marksman",
    "u6": "Marauder",
    "u7": "Ram",
    "u8": "Ballista",
    "u9": "Logades",
    "u10": "Settler",
    "hero": "Hero"
}

# Helper to get the name of the unit based on faction
def get_unit_name(unit_code: str, faction: str = "roman") -> str:
    if faction == "roman":
        units = roman_units
    elif faction == "gaul":
        units = gaul_units
    elif faction == "teuton":
        units = teuton_units
    elif faction == "egyptian":
        units = egyptian_units
    elif faction == "hun":
        units = hun_units
    else:
        return f"Unknown Faction ({unit_code})"

    return units.get(unit_code, f"Unknown Unit ({unit_code})")
