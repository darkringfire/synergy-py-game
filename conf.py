import utils as u

DEBUG = False
# DEBUG = True


class Params:
    max_health = u.PowerParam(10)
    capacity = u.LinearParam(1)
    speed = u.PowerParam(1.0, 1.2)
    fill_delay = u.PowerParam(1.0, 1)
    upgrade_delay = u.PowerParam(2.0, 1)
    heal_delay = u.PowerParam(2.0, 1)
    safe_delay = u.PowerParam(5.0, 0.9)
    upgrade_price = u.PowerParam(1000, 1.5)
    healing_price = u.PowerParam(500, 1.1)

    grow_delay = u.PowerParam(5.0, 1.1)
    grow_tree_n = u.PowerParam(10, 0.9)
    burn_delay = u.PowerParam(20.0, 0.9)
    fires_n = u.PowerParam(5, 1.1)
    tree_bonus = u.PowerParam(100, 1.2)
    burn_penalty = u.PowerParam(5, 2)

    clouds_delay = u.PowerParam(10.0, 1.1)
    clouds_probability = u.PowerParam(0.05, 1.1)
    thunder_probability = u.PowerParam(0.05, 1.1)


# Helicopter inits
HEALTH_INIT = 3
WATER_INIT = 0
SCORE_INIT = 0


# Map inits


# Clouds init
CLOUDS_DELAY = 10


# Tiles 🔲🟩🟦🌳🏥🏭🔥🚁👻💥💖💜💧💎 🍰🕑💢🏅
class T:
    i = [
        "🔲",
        "🟩",
        "🟦",
        "🌳",
        "🏥",
        "🏭",
        "🔥",
        "🚁",
        "👻",
        "💥",
        "💖",
        "💜",
        "💧",
        "💎",
        "🍰",
        "  ",
        "🕑",
        "💢",
        "🏅",
    ]

    EMPTY = 0
    GROUND = 1
    RIVER = 2
    TREE = 3
    HOSPITAL = 4
    WORKSHOP = 5
    FIRE = 6
    HELICOPTER = 7
    CLOUD = 8
    THUNDER = 9
    HEART = 10
    SAFE = 11
    WATER = 12
    GEM = 13
    UPGRADE = 14
    SPACE = 15
    CLOCK = 16
    LOSE = 17
    LEVEL = 18
