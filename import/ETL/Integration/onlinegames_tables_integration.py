import pandas as pd
import numpy as np
import re

from ETL.Integration.bgg_and_bga_integration import find_closest_match
from ETL.helper import import_json_to_dataframe, get_latest_version_of_file, export_df_to_csv, \
    import_pickle_to_dataframe, export_df_to_pickle

JACCARD_THRESHOLD_GAME_NAME = 0.301


def integrate_onlinegames_tables():
    onlinegames_filename = get_latest_version_of_file(
        '../Data/Onlinegames/Raw/Onlineboardgames_table_raw2.csv')

    onlinegames_df = pd.read_csv(onlinegames_filename, sep=';')
    # onlinegame_names = onlinegames_df['Name'].tolist()

    bgg_filename = get_latest_version_of_file(
        '../Data/BoardGameGeeks/Processed/GameInformation/01_BGG_Game_Information_*.csv')
    bgg_df = pd.read_csv(bgg_filename, index_col=0)
    bgg_names = bgg_df['name'].tolist()

    # Extract only games without BGG ID to match
    onlinegames_games_without_BGGID = onlinegames_df[onlinegames_df['BGGID'].isna()]
    onlinegame_names_without_BGGID = onlinegames_games_without_BGGID['Name'].tolist()

    # Find exact matches Onlingames - BGG
    exact_matches = list(set(bgg_names).intersection(set(onlinegame_names_without_BGGID)))

    # subtract exact matches from datasets:
    subset_bgg_df = bgg_df[~bgg_df['name'].isin(exact_matches)]
    subset_onlinegames_df = onlinegame_names_without_BGGID[~onlinegame_names_without_BGGID['Name'].isin(exact_matches)]
    subset_onlinegame_names_without_BGGID = subset_onlinegames_df['Name'].tolist()
    subset_bgg_df_names = subset_bgg_df['name'].tolist()

    # Match left over names Onlinegames - BGG
    match_list = []

    for name in subset_onlinegame_names_without_BGGID:
        match = find_closest_match(name, subset_bgg_df_names, JACCARD_THRESHOLD_GAME_NAME)
        match_list.append(
            {'online_name': name, 'bgg_name': match['name'], 'Jaccard_score': match['jaccard_score']}
        )
    matches_df = pd.DataFrame(match_list)
    print("Test")
