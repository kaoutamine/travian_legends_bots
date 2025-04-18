# oasis.py

def filter_oases(farms: list) -> list:
    """
    Filters only Oasis type targets from parsed farm list.
    Oasis = target.type == 2
    """
    return [farm for farm in farms if farm['type'] == 'Oasis']


def sort_oases_by_loot(oases: list) -> list:
    """
    Sorts oases from most loot to least loot.
    """
    return sorted(oases, key=lambda o: o['total_loot'], reverse=True)


def best_oasis(oases: list) -> dict:
    """
    Returns the oasis with the highest loot.
    """
    if not oases:
        return None
    return max(oases, key=lambda o: o['total_loot'])
