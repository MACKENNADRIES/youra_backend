def get_aura_level(points):
    # Defining ranges for 10 levels with descriptive names and colors
    aura_levels = [
        (range(0, 100), "Initiator", "#FFD700"),  # Gold
        (range(101, 200), "Sustainer", "#00FF00"),  # Green
        (range(201, 300), "Visionary", "#1E90FF"),  # Dodger Blue
        (range(301, 400), "Creator", "#FF4500"),  # Orange Red
        (range(401, 500), "Innovator", "#9400D3"),  # Dark Violet
        (range(501, 600), "Accelerator", "#00CED1"),  # Dark Turquoise
        (range(601, 700), "Transformer", "#FF69B4"),  # Hot Pink
        (range(701, 800), "Healer", "#7FFF00"),  # Chartreuse
        (range(801, 900), "Orchestrator", "#FF8C00"),  # Dark Orange
        (range(901, 10000), "Harmoniser", "#FFFFFF"),  # White (ethereal glow)
    ]

    # Iterate through the levels and check if the user's points fall within a range
    for point_range, level, color in aura_levels:
        if points in point_range:
            # Return the descriptive level, badge image, and glow color
            badge_image = f"/images/{level.lower().replace(' ', '-')}.png"
            return {
                "level": level,
                "badgeImage": badge_image,
                "glowColor": color,
            }

    # If no level found, return None
    return None
