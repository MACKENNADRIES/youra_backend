def get_aura_level(points):
    # Defining ranges for 10 levels with descriptive names
    aura_levels = [
        (range(0, 100), "Initiator"),
        (range(101, 200), "Sustainer"),
        (range(201, 300), "Visionary"),
        (range(301, 400), "Creator"),
        (range(401, 500), "Innovator"),
        (range(501, 600), "Accelerator"),
        (range(601, 700), "Transformer"),
        (range(701, 800), "Healer"),
        (range(801, 900), "Orchestrator"),
        (range(901, 10000), "Harmoniser"),
    ]

    # Iterate through the levels and check if the user's points fall within a range
    for point_range, level in aura_levels:
        if points in point_range:
            # Return the descriptive level and the corresponding badge image path
            badge_image = f"/images/{level.lower().replace(' ', '-')}.png"
            return {"level": level, "badgeImage": badge_image}

    # If no level found, return None
    return None
