# osbc-scripts<br />
pasted together python scripts<br />

Includes functions and code from: https://github.com/WillowsDad<br />
Place file in OSRS-Bot-COLOR/src/model/osrs<br />
In OSRS-Bot-COLOR/src/model/osrs/__init__.py add: from .culinary import OSRSCulinary<br />
In NPC Indicators plugin make the color PINK and the border 7<br />
In Object Markers plugin make the color CYAN and the border 7<br />
In OSRS-Bot-COLOR/src/utilities/api/item_ids.py add<br />

burnt_food = [<br />
    BURNT_FISH,<br />
    BURNT_FISH_343,<br />
    BURNT_FISH_357,<br />
    BURNT_FISH_367,<br />
    BURNT_FISH_369,<br />
    BURNT_SWORDFISH,<br />
    BURNT_LOBSTER,<br />
    BURNT_SHARK,<br />
    BURNT_MANTA_RAY,<br />
    BURNT_SEA_TURTLE,<br />
    BURNT_PITTA_BREAD,<br />
    BURNT_CAKE,<br />
    BURNT_STEW,<br />
    BURNT_CURRY,<br />
    BURNT_CHICKEN,<br />
    BURNT_MEAT,<br />
    BURNT_BATTA,<br />
    BURNT_PIZZA,<br />
    BURNT_BREAD,<br />
    BURNT_PIE,<br />
    BURNT_KARAMBWAN,<br />
    BURNT_POTATO,<br />
    BURNT_RABBIT,<br />
    BURNT_MONKFISH,<br />
    BURNT_SHRIMP,<br />
    BURNT_DARK_CRAB,<br />
    BURNT_ANGLERFISH,<br />
    BURNT_FISH_20854,<br />
    BURNT_FISH_23873,<br />
    TROUT,<br />
    SALMON,<br />
]

Known issues: Has to click twice to begin cooking. Requires 26 raw_fish or 26 burnt_food to operate.
