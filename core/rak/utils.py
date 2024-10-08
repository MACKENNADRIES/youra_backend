def get_aura_level(points):
    aura_levels = [
        (range(0, 100), "Generator", "Initiator", "Warm Yellow"),
        (range(100, 200), "Generator", "Sustainer", "Golden Yellow"),
        (range(200, 300), "Generator", "Visionary", "Amber"),
        (range(300, 400), "Generator", "Creator", "Deep Orange"),
        (range(400, 500), "Manifesting Generator", "Accelerator", "Bright Red"),
        (range(500, 600), "Manifesting Generator", "Multitasker", "Coral Red"),
        (range(600, 700), "Manifesting Generator", "Problem Solver", "Burgundy"),
        (range(700, 800), "Manifesting Generator", "Transformer", "Crimson"),
        (range(800, 900), "Projector", "Guide", "Sky Blue"),
        (range(900, 1000), "Projector", "Teacher", "Navy Blue"),
        (range(1000, 1100), "Projector", "Healer", "Indigo"),
        (range(1100, 1200), "Projector", "Orchestrator", "Royal Blue"),
        (range(1200, 1300), "Manifestor", "Instigator", "Olive Green"),
        (range(1300, 1400), "Manifestor", "Leader", "Emerald Green"),
        (range(1400, 1500), "Manifestor", "Independent", "Dark Teal"),
        (range(1500, 1600), "Manifestor", "Creator", "Deep Forest Green"),
        (range(1600, 1700), "Reflector", "Observer", "Light Silver"),
        (range(1700, 1800), "Reflector", "Analyzer", "Soft Grey"),
        (range(1800, 1900), "Reflector", "Balancer", "Pearl White")
    ]

    for point_range, main_level, sub_level, color in aura_levels:
        if points in point_range:
            return {
                "main_level": main_level,
                "sub_level": sub_level,
                "color": color
            }

    # Handling points above 1900 manually, since range cannot cover float('inf')
    if points >= 1900:
        return {
            "main_level": "Reflector",
            "sub_level": "Harmonizer",
            "color": "Crystal White"
        }

    return None