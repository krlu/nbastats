import json
import os
import time
from datetime import datetime

import requests
from basketball_reference_web_scraper import client, errors
from basketball_reference_web_scraper.data import OutputType, TEAM_NAME_TO_TEAM, Team


# https://jaebradley.github.io/basketball_reference_web_scraper/api/

def num_files_with_name(directory, name):
    i = 0
    for file_name in os.listdir(directory):
        f = os.path.join(directory, file_name)
        # checking if it is a file
        if os.path.isfile(f) and name in file_name:
            i += 1
    return i


def get_player_box_scores(year, output_dir, delay=3):
    """
    :param year: ending year of a particular season
    :param output_dir: directory for output files
    :param delay: time delay for endpoint querying (in seconds), default value 3
    :return: None
    """
    # get player for year
    players_in_season = client.players_season_totals(season_end_year=year)

    # create new directory for year
    new_dir = f"./{output_dir}/{year}"
    is_exist = os.path.exists(new_dir)
    if not is_exist:
        os.makedirs(new_dir)

    # get data for each player
    prev_slug = ""
    for player in players_in_season:
        slug = player['slug']
        name = player['name']
        if slug != prev_slug:
            print((year, name))
            num_files = num_files_with_name(new_dir, name)
            if num_files == 0:
                print("getting regular season data...")
                time.sleep(delay)
                player_file_name1 = f"./{output_dir}/{year}/{year - 1}_{year}_{name}_regular_season_box_scores.json"
                player_box_score_regular_season(slug, year, player_file_name1)
                # num_files = num_files_with_name(new_dir, name)
                # if num_files == 1:
                time.sleep(delay)
                print("getting playoff data...")
                player_file_name2 = f"./{output_dir}/{year}/{year - 1}_{year}_{name}_playoffs_box_scores.json"
                player_box_score_playoffs(slug, year, player_file_name2)
        prev_slug = slug


def player_box_score_regular_season(slug, year, player_file_name, delay=3):
    """
    :param slug: identifier string for a player
    :param year: ending year for season
    :param player_file_name: output file for json data
    :param delay: time delay for endpoint querying (in seconds), default value 3
    :return: None
    """
    try:
        client.regular_season_player_box_scores(
            player_identifier=slug,
            season_end_year=year,
            output_type=OutputType.JSON,
            output_file_path=player_file_name
        )
    except requests.exceptions.HTTPError:
        print("re-trying..........")
        time.sleep(delay)
        player_box_score_regular_season(slug, year, player_file_name)


def player_box_score_playoffs(slug, year, player_file_name, delay=3):
    """
    :param slug: identifier string for a player
    :param year: ending year for season
    :param player_file_name: output file for json data
    :param delay: time delay for endpoint querying (in seconds), default value 3
    :return: None
    """
    try:
        client.playoff_player_box_scores(
            player_identifier=slug,
            season_end_year=year,
            output_type=OutputType.JSON,
            output_file_path=player_file_name
        )
    except (requests.exceptions.HTTPError, errors.InvalidPlayerAndSeason, AttributeError) as error:
        if type(error) == errors.InvalidPlayerAndSeason:
            print("player was not in playoffs")
        elif type(error) == AttributeError:
            print(error)
        else:
            print("re-trying..........")
            time.sleep(delay)
            player_box_score_playoffs(slug, year, player_file_name)


def get_all_player_box_scores_all_time(start_year, end_year):
    for year in range(end_year, start_year, -1):
        get_player_box_scores(year, "player_box_scores")


def get_all_team_schedules_all_time(start_year, end_year, output_dir="schedules"):
    new_dir = f"./{output_dir}/"
    is_exist = os.path.exists(new_dir)
    if not is_exist:
        os.makedirs(new_dir)
    for year in range(end_year, start_year, -1):
        print(year)
        time.sleep(60)
        client.season_schedule(
            season_end_year=year,
            output_type=OutputType.JSON,
            output_file_path=f"{new_dir}/{year - 1}_{year}_season.json"
        )


def get_schedule(year):
    with open(f'./schedules/{year - 1}_{year}_season.json') as f:
        d = json.load(f)
        return d


def get_all_team_box_scores(year, output_dir="team_box_scores"):
    new_dir = f"./{output_dir}/{year}"
    is_exist = os.path.exists(new_dir)
    if not is_exist:
        os.makedirs(new_dir)
    schedules = get_schedule(year)
    prev_game_date = ""
    for game in schedules:
        game_time = game['start_time']
        game_date = game_time.split("T")[0]
        if game_date != prev_game_date:
            time.sleep(30)
            datetime_object = datetime.strptime(game_date, '%Y-%m-%d')
            client.team_box_scores(
                day=datetime_object.day,
                month=datetime_object.month,
                year=datetime_object.year,
                output_type=OutputType.JSON,
                output_file_path=f"{new_dir}/{datetime_object.day}_{datetime_object.month}_{year}_box_scores.json"
            )
        print(game_date)
        prev_game_date = game_date


def get_team_play_by_play(start_year, end_year):
    for year in range(end_year, start_year-1, -1):
        get_team_play_by_play_by_year(year)


def get_team_play_by_play_by_year(year, output_dir="team_play_by_play", min_date=None, delay=15):
    """
    :param year: Ending year of season
    :param delay: time delay for endpoint querying (in seconds), default value 15
    :param output_dir: Directory for all play by play data - defaults to "./team_play_by_play
    :return: None
    """
    new_dir = f"./{output_dir}/{year}"
    is_exist = os.path.exists(new_dir)
    if not is_exist:
        os.makedirs(new_dir)
    schedules = get_schedule(year)
    prev_game_date = ""
    for game in schedules:
        game_time = game['start_time']
        game_date = game_time.split("T")[0]
        if game_date != prev_game_date:
            print(game)
            home_team_str = game['home_team']
            away_team_str = game['away_team']
            datetime_object = datetime.strptime(game_date, '%Y-%m-%d')
            day = datetime_object.day
            month = datetime_object.month
            if min_date is not None and f"{year}_{month}_{day}" < min_date:
                pass
            else:
                time.sleep(delay)
                get_pbp_helper(home_team_str, away_team_str, datetime_object.year, month, day, new_dir)


def get_pbp_helper(home_team_str, away_team_str, year, month, day, out_dir, day_offset=0, is_negative=True):
    signed_offset = day_offset * (-1 if is_negative else 1)
    try:
        file_name = f"{year}_{month}_{day + signed_offset}_{home_team_str}_{away_team_str}_pbp.json"
        home_team = TEAM_NAME_TO_TEAM[home_team_str]
        client.play_by_play(
            home_team=home_team,
            year=year,
            month=month,
            day=day + signed_offset,
            output_type=OutputType.JSON,
            output_file_path=f"{out_dir}/{file_name}"
        )
    except errors.InvalidDate as error:
        print(error)
        if day_offset < 3:  # 3 hard coded as maximum offset of days to search for data
            new_offset = day_offset + (0 if is_negative else 1)
            print(f"retrying finding game with offset {new_offset}")
            get_pbp_helper(home_team_str, away_team_str, year, month, day, out_dir, new_offset, not is_negative)


get_team_play_by_play(1985, 2018)