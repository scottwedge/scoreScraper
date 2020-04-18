import dataclasses
from datetime import datetime


@dataclass
class Seasons:
    season_info = {
        "18-19": {
            "regular_season_start": datetime(),
            "regular_season_end": datetime(),
            "post_season_start": datetime(),
            "post_season_end": "",
        }
    }
