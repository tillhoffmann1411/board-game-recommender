import pandas as pd
import numpy as np
import re

from ETL.Integration.bgg_and_bga_integration import find_match
from ETL.helper import import_json_to_dataframe, get_latest_version_of_file, export_df_to_csv, \
    import_pickle_to_dataframe, export_df_to_pickle

JACCARD_THRESHOLD_GAME_NAME = 0.6


def merge_online_games():
    # import all online game csvs to dataframes
    yucata_scrape_filename = get_latest_version_of_file('../Data/Onlinegames/Yucata/Raw/Yucata_all_data_raw.csv')
    yucata_scrape_df = pd.read_csv(yucata_scrape_filename, sep=';')
    boardgamearena_scrape_filename = get_latest_version_of_file(
        '../Data/Onlinegames/Boardgamearena/Raw/Boardgamearena_all_data_raw.csv')
    boardgamearena_scrape_df = pd.read_csv(boardgamearena_scrape_filename, sep=';')
    tabletopia_scrape_filename = get_latest_version_of_file(
        '../Data/Tabletopia/Tabletopia/Raw/tabletopia_all_data_raw.csv')
    tabletopia_scrape_df = pd.read_csv(tabletopia_scrape_filename, sep=',')

    # drop potential duplicates
    yucata_scrape_df.drop_duplicates(inplace=True)
    boardgamearena_scrape_df.drop_duplicates(inplace=True)
    tabletopia_scrape_df.drop_duplicates(inplace=True)

    # rename columns
    yucata_scrape_df.rename(columns={'YucataName': 'Name', 'YucataPlayers': 'yucata_players', 'YucataTime': 'playtime',
                                     'YucataAuthor': 'yucata_author', 'YucataLink': 'Onlinegamelink', 'YucataBoardGameGeekIF': 'BGGID'}, inplace=True)
    boardgamearena_scrape_df.rename(columns={'game_name_boardgamearena': 'Name', 'game_url_boardgamearena': 'Onlinegamelink'},
                                    inplace=True)
    tabletopia_scrape_df.rename(
        columns={'game_name_tabletopia': 'Name', 'game_url_tabletopia': 'Onlinegamelink', 'bgg_link_tabletopia': 'bgg_url',
                 }, inplace=True)

    # Add origin of data as text
    Origin = 'Yucata'
    yucata_scrape_df['Origin'] = Origin
    Origin = 'Boardgamearena'
    boardgamearena_scrape_df['Origin'] = Origin
    Origin = 'Tabletopia'
    tabletopia_scrape_df['Origin'] = Origin

    # Extract BGG ID from dfs
    tabletopia_scrape_df['BGGID'] = tabletopia_scrape_df['bgg_url'].str.extract('e/(.+?)/')

    # Set Delete unnecessary columns and rename all atrributes to be the same
    yucata_scrape_df = yucata_scrape_df.drop(['yucata_players', 'playtime', 'YucataAge', 'yucata_author', 'YucataIllustrator', 'YucataPublisher', 'YucataDeveloper', 'YucataOnlinesince'], 1)
    boardgamearena_scrape_df = boardgamearena_scrape_df.drop(columns=['number_players_boardgamearena', 'playing_time_boardgamearena', 'game_strategy_boardgamearena', 'game_interaction_boardgamearena', 'game_complexity_boardgamearena', 'game_luck_boardgamearena', 'rounds_played_boardgamearena', 'available_since_boardgamearena', 'version_boardgamearena', 'description_boardgamearena', 'author_name_boardgamearena', 'graphicer_name_boardgamearena', 'publisher_name_boardgamearena', 'basegame_release_year_boardgamearena', 'developer_name_boardgamearena'])
    tabletopia_scrape_df = tabletopia_scrape_df.drop(columns=['player_min_age_tabletopia', 'number_players_tabletopia', 'playing_time_tabletopia', 'rating_tabletopia', 'designer_tabletopia', 'illustrator_tabletopia', 'publisher_tabletopia', 'author_tabletopia', 'genre_tabletopia', 'description_tabletopia', 'bgg_url'])


    # merge dataframes
    onlinegames_merge_df = pd.DataFrame(columns=['Name', 'Onlinegamelink', 'Origin', 'BGGID'])
    onlinegames_merge_df = onlinegames_merge_df.append(yucata_scrape_df)
    onlinegames_merge_df = onlinegames_merge_df.append(boardgamearena_scrape_df)
    onlinegames_merge_df = onlinegames_merge_df.append(tabletopia_scrape_df)

    # create primary keys
    onlinegames_merge_df.insert(0, 'Onlinegamelink ID', range(1, 1 + len(onlinegames_merge_df)))

    # export dataframe
    export_path = '../Data/Onlinegames/Raw/Onlineboardgames_table_raw.csv'
    onlinegames_merge_df.to_csv(export_path, na_rep='NULL', sep=';')



def match_online_game_names_and_bgg_names():
    onlinegames_filename = get_latest_version_of_file(
        '../Data/Onlinegames/Raw/Onlineboardgames_table_raw.csv')

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
        match = find_match(name, subset_bgg_df_names, JACCARD_THRESHOLD_GAME_NAME)
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
    merge_2 = merge_2[['Onlinegamelink ID', 'Name', 'Onlinegamelink', 'Origin', 'BGGID']]

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
                                   'Origin': 'origin', 'BGGID': 'bgg_id'}, inplace=True)
    onlinegames_df = onlinegames_df.drop(columns={'Unnamed: 0'})

    # If bgg_id has to be int (Beware of nAn conversion!)
    #onlinegames_df['bgg_id'] = onlinegames_df['bgg_id'].fillna(0.0).astype(int)
    #onlinegames_df['bgg_id'] = onlinegames_df['bgg_id'].astype(int)

    # drop online games without bgg_id:
    onlinegames_df = onlinegames_df[~onlinegames_df['bgg_id'].isna()]

    # export result to csv:
    export_path = '../Data/Onlinegames/Processed/online_games.csv'
    export_df_to_csv(onlinegames_df, export_path)
