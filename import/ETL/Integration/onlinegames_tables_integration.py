import pandas as pd
import numpy as np
import re

from ETL.Integration.bgg_and_bga_integration import find_closest_match
from ETL.helper import import_json_to_dataframe, get_latest_version_of_file, export_df_to_csv, \
    import_pickle_to_dataframe, export_df_to_pickle

JACCARD_THRESHOLD_GAME_NAME = 0.6


def integrate_online_games():
    merge_online_games()
    match_online_game_names_and_bgg_names()


def merge_online_games():
    # import all online game csvs to dataframes

    # drop potential duplicates

    # rename columns

    # merge dataframes

    # extract ids

    # create primary keys

    # export dataframe

    pass


def match_online_game_names_and_bgg_names():
    onlinegames_filename = get_latest_version_of_file(
        '../Data/Onlinegames/Raw/Onlineboardgames_table_raw2.csv')

    onlinegames_df = pd.read_csv(onlinegames_filename, sep=';')

    bgg_filename = get_latest_version_of_file(
        '../Data/BoardGameGeeks/Processed/GameInformation/01_BGG_Game_Information_*.csv')
    bgg_df = pd.read_csv(bgg_filename, index_col=0)
    bgg_names = bgg_df['name'].tolist()

    # Extract only games without BGG ID to match
    onlinegames_games_without_BGGID = onlinegames_df[onlinegames_df['BGGID'].isna()]
    onlinegame_names_without_BGGID = onlinegames_games_without_BGGID['Name'].tolist()

    # Find exact matches Onlingames - BGG
    exact_matches = list(set(bgg_names).intersection(set(onlinegame_names_without_BGGID)))

    # Exact matches as list of dicts (can later be used to create a pd.DF)
    exact_matches_list_of_dict = [{'online_name': x, 'bgg_name': x} for x in exact_matches]

    # subtract exact matches from datasets:
    subset_bgg_df = bgg_df[~bgg_df['name'].isin(exact_matches)]
    subset_onlinegames_df = onlinegames_games_without_BGGID[
        ~onlinegames_games_without_BGGID['Name'].isin(exact_matches)]
    subset_onlinegame_names_without_BGGID = subset_onlinegames_df['Name'].tolist()
    subset_bgg_df_names = subset_bgg_df['name'].tolist()

    # Match left over names Onlinegames - BGG
    match_list = []

    for name in subset_onlinegame_names_without_BGGID:
        match = find_closest_match(name, subset_bgg_df_names, JACCARD_THRESHOLD_GAME_NAME)
        match_list.append(
            {'online_name': name, 'bgg_name': match['name'], 'jaccard_score': match['jaccard_score']}
        )

    # drop entries that could not be matched:
     match_list = [x for x in match_list if x['jaccard_score'] != '']

    # add exact matches to match_list:
    match_list = match_list + exact_matches_list_of_dict

    matches_df = pd.DataFrame(match_list)

    # merge matches and bgg to get bgg ids:
    merge_1 = pd.merge(left=matches_df, right=bgg_df,
                       left_on='bgg_name', right_on='name')
    matches_df = merge_1[['bgg_name', 'online_name', 'bgg_game_id']]

    # merge matches and online games df:
    merge_2 = pd.merge(left=onlinegames_games_without_BGGID, right=matches_df,
                       left_on='Name', right_on='online_name')
    merge_2['BGGID'] = merge_2['bgg_game_id']

    # keep only columns from original online games df:
    merge_2 = merge_2.iloc[:, 0:5]

    # create a temp_df that contains all games out of the online games df that were not matched in the process
    # (the ones that had been matched previously and the ones that could not be matched in the process)
    temp_df = onlinegames_df[~onlinegames_df['Onlinegamelink ID'].isin(merge_2['Onlinegamelink ID'].tolist())]

    # combine both to get the full dataset with the additional information about the bgg_game_ids out of the games that
    # were successfully matched:
    onlinegames_df = pd.concat([temp_df, merge_2])
    onlinegames_df.drop_duplicates(subset=['Onlinegamelink ID'], inplace=True)

    ## export online games:
    # rename a few columns
    onlinegames_df.rename(columns={'Name': 'name', 'Onlinegamelink ID': 'online_game_id', 'Onlinegamelink': 'url',
                                   'Origin': 'origin', 'BGGID': 'bgg_id' }, inplace=True)

    # export result to csv:
    export_path = '../Data/Onlinegames/Processed/online_games.csv'
    export_df_to_csv(onlinegames_df, export_path)
