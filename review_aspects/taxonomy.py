ASPECT_GROUPS = {
    "Food": [
        "Taste / seasoning",
        "Texture / doneness",
        "Temperature / freshness",
        "Portion size",
        "General food comments",
    ],
    "Staff / service": ["Friendliness / helpfulness", "Communication", "Service speed"],
    "Price / value": ["Prices / charges", "Value for money"],
    "Wait times": ["Queue length / duration", "Queue movement"],
    "Atmosphere / facilities": ["Cleanliness", "Ambience", "Seating / crowding"],
    "Business operations": [
        "Parking / location",
        "Ordering / payment",
        "Takeout / packaging",
        "Entry rules",
    ],
    "Recommendations / loyalty": [
        "Recommendation",
        "Return intention",
        "Reputation / discovery",
    ],
    "Overall experience": ["General satisfaction"],
}

ASPECT_PARENTS = {
    f"{parent} / {child}": parent
    for parent, children in ASPECT_GROUPS.items()
    for child in children
}


def parent_categories(labels):
    return list(dict.fromkeys(ASPECT_PARENTS.get(label, label) for label in labels))
