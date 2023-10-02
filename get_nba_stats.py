from nba_api.stats.endpoints import playercareerstats, playbyplay, leaguegamelog
from nba_api.stats.static import players


def get_all_player_career_stats():
    all_players = players.get_players()
    player_stats = []
    for player in all_players:
        player_id = player['id']
        career = playercareerstats.PlayerCareerStats(player_id=player_id)
        career_dict = career.get_dict()
        player_stats.append({"player": player, "career": career_dict})


def process_player_career_stats(career_dict):
    for result in career_dict["resultSets"]:
        print(result["name"])
        print(result["headers"])
        print(result["rowSet"])
        print("--------------------")


def get_games():
    lgl = leaguegamelog.LeagueGameLog(season=2018)
    game_log_dict = lgl.get_dict()
    for result in game_log_dict["resultSets"]:
        print(result["name"])
        print(result["headers"])
        for row in result["rowSet"]:
            game_id = row[4]
            print(game_id)
            # pbp = playbyplay.PlayByPlay(game_id)
            # pbp_json = pbp.get_json()


from basketball_reference_web_scraper import client

players = client.players_season_totals(season_end_year=2018)

print(len(players))
