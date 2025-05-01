import os

def get_faction_name(faction_id: int) -> str:
    faction_mapping = {
        1: "roman",
        2: "teuton",
        3: "gaul",
        6: "egyptian",
        7: "hun"
    }

    if faction_id not in faction_mapping:
        this_file = os.path.abspath(__file__)
        raise ValueError(
            f"Unknown faction ID: {faction_id}. "
            f"To fix this, update the `faction_mapping` dictionary in:\n  {this_file}\n"
            f"Travian might have introduced a new tribe, or you might have a corrupted player profile."
        )
    return faction_mapping[faction_id]
