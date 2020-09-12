import scrapy


class Game(scrapy.Item):
    game_id = scrapy.Field()
    date = scrapy.Field()
    home_record = scrapy.Field()
    away_record = scrapy.Field()
    line = scrapy.Field()


class Record(scrapy.Item):
    wins = scrapy.Field()
    losses = scrapy.Field()


class Line(scrapy.Item):
    favorite = scrapy.Field()
    spread = scrapy.Field()
    ou = scrapy.Field()


class Team(scrapy.Item):
    location = scrapy.Field()
    name = scrapy.Field()

class TeamStats(scrapy.Item):
    team = scrapy.Field()
    game_id = scrapy.Field()
    home = scrapy.Field()
    fgm = scrapy.Field()
    fga = scrapy.Field()
    fg_per = scrapy.Field()
    x3pa = scrapy.Field()
    x3pm = scrapy.Field()
    x3p_per = scrapy.Field()
    fta = scrapy.Field()
    ftm = scrapy.Field()
    ft_per = scrapy.Field()
    oreb = scrapy.Field()
    dreb = scrapy.Field()
    reb = scrapy.Field()
    ast = scrapy.Field()
    stl = scrapy.Field()
    blk = scrapy.Field()
    to = scrapy.Field()
    pf = scrapy.Field()
    pts = scrapy.Field()
    x1q_pts = scrapy.Field()
    x2q_pts = scrapy.Field()
    x3q_pts = scrapy.Field()
    x4q_pts = scrapy.Field()
    ot_pts = scrapy.Field()
    pace = scrapy.Field()  # Four Factor Table
    efg_per = scrapy.Field()
    to_per = scrapy.Field()  # Four Factor Table
    orb_per = scrapy.Field()
    ft_per_fga = scrapy.Field()  # Four Factor table
    off_rating = scrapy.Field()
    ts_per = scrapy.Field()
    x3p_ar = scrapy.Field()
    ft_ar = scrapy.Field()
    oreb_per = scrapy.Field()
    dreb_per = scrapy.Field()
    reb_per = scrapy.Field()
    ast_per = scrapy.Field
    stl_per = scrapy.Field()
    blk_per = scrapy.Field()
    tov_per = scrapy.Field()
    usg_per = scrapy.Field()
    off_rating = scrapy.Field()
    def_rating = scrapy.Field()
    bpm = scrapy.Field()


class Player(scrapy.Item):
    player_id = scrapy.Field()
    first_name = scrapy.Field()
    last_name = scrapy.Field()
    position = scrapy.Field()


class PlayerStats(scrapy.Item):
    player = scrapy.Field()
    game_id = scrapy.Field()
    min = scrapy.Field()
    fgm = scrapy.Field()
    fga = scrapy.Field()
    fg_per = scrapy.Field()
    x3pa = scrapy.Field()
    x3pm = scrapy.Field()
    x3p_per = scrapy.Field()
    fta = scrapy.Field()
    ftm = scrapy.Field()
    ft_per = scrapy.Field()
    oreb = scrapy.Field()
    dreb = scrapy.Field()
    reb = scrapy.Field()
    ast = scrapy.Field()
    stl = scrapy.Field()
    blk = scrapy.Field()
    to = scrapy.Field()
    pf = scrapy.Field()
    plusminus = scrapy.Field()
    pts = scrapy.Field()
    ts_per = scrapy.Field()
    efg_per = scrapy.Field()
    x3p_ar = scrapy.Field()
    ft_ar = scrapy.Field()
    oreb_per = scrapy.Field()
    dreb_per = scrapy.Field()
    reb_per = scrapy.Field()
    ast_per = scrapy.Field()
    stl_per = scrapy.Field()
    blk_per = scrapy.Field()
    tov_per = scrapy.Field()
    usg_per = scrapy.Field()
    off_rating = scrapy.Field()
    def_rating = scrapy.Field()
    bpm = scrapy.Field()
