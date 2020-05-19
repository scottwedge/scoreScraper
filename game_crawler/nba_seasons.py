from dataclasses import dataclass
from datetime import datetime


@dataclass
class Seasons:
    season_info = {
        "01-02": {
            "regular_season_start": datetime(2001, 10, 30),
            "regular_season_end": datetime(2002, 4, 17),
            "post_season_start": datetime(2002, 4, 20),
            "post_season_end": datetime(2002, 6, 12),
        },
        "02-03": {
            "regular_season_start": datetime(2002, 10, 29),
            "regular_season_end": datetime(2003, 4, 16),
            "post_season_start": datetime(2003, 4, 19),
            "post_season_end": datetime(2003, 6, 15),
        },
        "03-04": {
            "regular_season_start": datetime(2003, 10, 28),
            "regular_season_end": datetime(2004, 4, 14),
            "post_season_start": datetime(2004, 4, 17),
            "post_season_end": datetime(2004, 6, 15),
        },
        "04-05": {
            "regular_season_start": datetime(2004, 11, 2),
            "regular_season_end": datetime(2005, 4, 20),
            "post_season_start": datetime(2005, 4, 23),
            "post_season_end": datetime(2005, 6, 23),
        },
        "05-06": {
            "regular_season_start": datetime(2005, 11, 1),
            "regular_season_end": datetime(2006, 4, 19),
            "post_season_start": datetime(2006, 4, 22),
            "post_season_end": datetime(2006, 6, 3),
        },
        "06-07": {
            "regular_season_start": datetime(2006, 10, 31),
            "regular_season_end": datetime(2007, 4, 18),
            "post_season_start": datetime(2007, 4, 21),
            "post_season_end": datetime(2007, 6, 14),
        },
        "07-08": {
            "regular_season_start": datetime(2007, 10, 30),
            "regular_season_end": datetime(2008, 4, 16),
            "post_season_start": datetime(2008, 4, 19),
            "post_season_end": datetime(2008, 6, 17),
        },
        "08-09": {
            "regular_season_start": datetime(2008, 10, 28),
            "regular_season_end": datetime(2009, 4, 16),
            "post_season_start": datetime(2009, 4, 18),
            "post_season_end": datetime(2009, 6, 14),
        },
        "09-10": {
            "regular_season_start": datetime(2009, 10, 27),
            "regular_season_end": datetime(2010, 4, 14),
            "post_season_start": datetime(2010, 4, 17),
            "post_season_end": datetime(2010, 6, 17),
        },
        "10-11": {
            "regular_season_start": datetime(2010, 10, 26),
            "regular_season_end": datetime(2011, 4, 13),
            "post_season_start": datetime(2011, 4, 16),
            "post_season_end": datetime(2011, 6, 12),
        },
        "11-12": {
            "regular_season_start": datetime(2011, 12, 25),
            "regular_season_end": datetime(2012, 4, 26),
            "post_season_start": datetime(2012, 4, 28),
            "post_season_end": datetime(2012, 6, 21),
        },
        "12-13": {
            "regular_season_start": datetime(2012, 10, 30),
            "regular_season_end": datetime(2013, 4, 17),
            "post_season_start": datetime(2013, 4, 20),
            "post_season_end": datetime(2013, 6, 20),
        },
        "13-14": {
            "regular_season_start": datetime(2013, 10, 29),
            "regular_season_end": datetime(2014, 4, 16),
            "post_season_start": datetime(2014, 4, 19),
            "post_season_end": datetime(2014, 6, 15),
        },
        "14-15": {
            "regular_season_start": datetime(2014, 10, 28),
            "regular_season_end": datetime(2015, 4, 15),
            "post_season_start": datetime(2015, 4, 18),
            "post_season_end": datetime(2015, 6, 16),
        },
        "15-16": {
            "regular_season_start": datetime(2015, 10, 27),
            "regular_season_end": datetime(2016, 4, 13),
            "post_season_start": datetime(2016, 4, 16),
            "post_season_end": datetime(2016, 6, 19),
        },
        "16-17": {
            "regular_season_start": datetime(2016, 10, 25),
            "regular_season_end": datetime(2017, 4, 12),
            "post_season_start": datetime(2017, 4, 15),
            "post_season_end": datetime(2017, 6, 12),
        },
        "17-18": {
            "regular_season_start": datetime(2017, 10, 17),
            "regular_season_end": datetime(2018, 4, 11),
            "post_season_start": datetime(2018, 4, 14),
            "post_season_end": datetime(2018, 6, 8),
        },
        "18-19": {
            "regular_season_start": datetime(2016, 10, 16),
            "regular_season_end": datetime(2017, 4, 10),
            "post_season_start": datetime(2017, 4, 13),
            "post_season_end": datetime(2017, 6, 13),
        },
    }
