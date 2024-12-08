def get_aura_level(points):
    # Defining ranges for 10 levels with descriptive names and colors
    aura_levels = [
    (range(0, 100), "Initiator", "#00FF00"),  # Green
(range(101, 200), "Sustainer", "#FFD700"),  # Yellow
(range(201, 300), "Visionary", "#1E90FF"),  # Electric Blue
(range(301, 400), "Creator", "#FF00FF"),  # Magenta
(range(401, 500), "Innovator", "#FF0000"),  # Bright Red
(range(501, 600), "Accelerator", "#FFA500"),  # Orange
(range(601, 700), "Transformer", "#8B0000"),  # Deep Red
(range(701, 800), "Healer", "#40E0D0"),  # Turquoise
(range(801, 900), "Orchestrator", "#C0C0C0"),  # Silver
(range(901, 10000), "Harmoniser", "#800080"),  # Purple
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
