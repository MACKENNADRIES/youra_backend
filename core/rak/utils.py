# use this for points details

def get_aura_level(points):
    aura_levels = [
        # Generator (The Masterful Creator)
        (range(0, 40), "Generator", "Initiator", "Light Yellow"),
        (range(41, 100), "Generator", "Sustainer", "Golden Yellow"),
        (range(101, 170), "Generator", "Visionary", "Amber"),
        (range(170, 250), "Generator", "Creator", "Deep Orange"),
        # Manifesting Generator (The Impacting Creator)
        (range(251, 350), "Manifesting Generator", "Accelerator", "Bright Red"),
        (range(351, 450), "Manifesting Generator", "Multitasker", "Coral Red"),
        (range(451, 550), "Manifesting Generator", "Problem Solver", "Burgundy"),
        (range(551, 650), "Manifesting Generator", "Transformer", "Crimson"),
        # Projector (The Wisdom Keeper)
        (range(651, 800), "Projector", "Guide", "Sky Blue"),
        (range(800, 950), "Projector", "Teacher", "Navy Blue"),
        (range(951, 1100), "Projector", "Healer", "Indigo"),
        (range(1101, 1250), "Projector", "Orchestrator", "Royal Blue"),
        # Manifestor (The Force of Nature)
        (range(1251, 1500), "Manifestor", "Instigator", "Olive Green"),
        (range(1501, 1750), "Manifestor", "Leader", "Emerald Green"),
        (range(1751, 2000), "Manifestor", "Independent", "Dark Teal"),
        (range(2001, 2250), "Manifestor", "Creator", "Deep Forest Green"),
        # Reflector (The Sacred Mirror)
        (range(2251, 2750), "Reflector", "Observer", "Light Silver"),
        (range(2751, 3250), "Reflector", "Analyzer", "Soft Grey"),
        (range(3251, 5000), "Reflector", "Balancer", "Pearl White"),
        (range(5001, 6000), "Reflector", "Harmonizer", "Crystal White"),
    ]

    # Iterate through the levels and check if the user's points fall within a range
    for point_range, main_level, sub_level, color in aura_levels:
        if points in point_range:
            return {"main_level": main_level, "sub_level": sub_level, "color": color}

    # Handling points above 2000 manually
    if points >= 6000:
        return {
            "main_level": "Reflector",
            "sub_level": "Harmonizer",
            "color": "Crystal White",
        }

    # Default return in case points do not fall into any range
    return None
