"""
Shared constants for Business Planner domain.

Contains business names, priority mappings, and other shared constants
used across multiple services.
"""

# Business ID to name mapping
BUSINESS_NAMES = {
    1: "МАСТЕРСКАЯ INVENTUM",
    2: "ЛАБОРАТОРИЯ INVENTUM LAB",
    3: "R&D",
    4: "TRADE"
}

# Priority ID to emoji mapping
PRIORITY_CIRCLES = {
    1: "🔴",  # Высокий - Red
    2: "🟡",  # Средний - Yellow
    3: "🟢",  # Низкий - Green
    4: "⚪"   # Отложенный - White
}

# Priority ID to name mapping
PRIORITY_NAMES = {
    1: "Высокий",
    2: "Средний",
    3: "Низкий",
    4: "Отложенный"
}
