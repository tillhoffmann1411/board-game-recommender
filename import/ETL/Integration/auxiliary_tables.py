import pandas as pd
import numpy as np
import os
import json
import glob
from datetime import datetime

from ETL.Integration.bgg_and_bga_integration import find_closest_match
from ETL.helper import import_json_to_dataframe, export_df_to_json, export_df_to_csv, \
    get_latest_version_of_file, get_bga_publishers
from ETL.Scraper.spiders.bga_spiders import scrape_publishers


def auxiliary_tables():
    # 1) Publishers
    integrate_publishers()

    # 2) Designers

    # 3) Mechanics
    integrate_mechanics()

    # 4) Categories
    integrate_categories()

    # 5) Names



def integrate_publishers():
    # create a list of all unique bga publishers, including their id and the bga publisher url
    create_list_of_all_bga_publishers()

    # scrape the publisher names from BGA
    scrape_publishers()

def integrate_mechanics():
    # normalize bga_game_mechanics_relation table:
    normalize_bga_game_mechanics_relation()

    # normalize bga_game_mechanics_relation table:
    normalize_bgg_game_mechanics_relation()

    # match and merge bga and bgg mechanics using jaccard string matching on mechanic names:
    match_and_merge_bga_and_bgg_mechanics()

    # replace bga and bgg ids with new mechanics_key in relation tables and mechanics table
    # and then concat bga and bgg relation tables to one table
    replace_old_ids_with_new_key_and_concatenate_mechanic_relation_tables()


def integrate_categories():
    # normalize bga_game_categories_relation table:
    normalize_bga_game_categories_relation()

    # normalize bga_game_categories_relation table:
    normalize_bgg_game_categories_relation()

    # match and merge bga and bgg categories using jaccard string matching on category names:
    match_and_merge_bga_and_bgg_categories()

    # replace bga and bgg ids with new categories_key in relation tables and categories table
    # and then concat bga and bgg relation tables to one table
    replace_old_ids_with_new_key_and_concatenate_category_relation_tables()




def normalize_bga_game_mechanics_relation():
    # import bga_games_mechanic_relation:
    mechanics_bga_games_relation_path_fuzzy = '../Data/BoardGameAtlas/Processed/API/04_BGA_Game_Mechanics_Relation_*.json'
    mechanics_bga_games_relation_path = get_latest_version_of_file(mechanics_bga_games_relation_path_fuzzy)
    mechanics_bga_games_relation_df = import_json_to_dataframe(mechanics_bga_games_relation_path)

    # import bga mechanics:
    mechanics_bga = pd.read_csv('../Data/BoardGameAtlas/Raw/API/Mechanics/all_bga_mechanics.csv', index_col=0)

    # import game keys:
    game_keys = pd.read_csv('../Data/Joined/Integration/GameKeys/Keys_All_Games_Integrated.csv', index_col=0)

    # join games_mechanic_relation table to replace bga_game_id column with game_keys column:
    mechanics_bga_games_relation_df = pd.merge(left=mechanics_bga_games_relation_df, right=game_keys,
                                               left_on='game_id', right_on='bga_game_id')

    # normalize by only keeping game_key and mechanic_id
    mechanics_bga_games_relation_df = mechanics_bga_games_relation_df[['game_key', 'mechanic_id']]

    # export df
    export_path = '../Data/BoardGameAtlas/Processed/API/04_BGA_Game_Mechanics_Relation_Cleaned.csv'
    export_df_to_csv(mechanics_bga_games_relation_df, export_path)


def normalize_bgg_game_mechanics_relation():
    # import bgg games:
    mechanics_bgg_games_relation_path_fuzzy = '../Data/BoardGameGeeks/Processed/GameInformation/04_BGG_Game_Mechanic_Relation_*.csv'
    mechanics_bgg_games_relation_path = get_latest_version_of_file(mechanics_bgg_games_relation_path_fuzzy)
    mechanics_bgg_games_relation_df = pd.read_csv(mechanics_bgg_games_relation_path, index_col=0)

    # create mechanics list:
    mechanics_bgg = pd.DataFrame(mechanics_bgg_games_relation_df['mechanic_name'].drop_duplicates())

    # create temporary key_column:
    mechanics_bgg.insert(0, 'bgg_mechanic_key', range(1001, 1001 + len(mechanics_bgg)))

    # import game keys:
    game_keys = pd.read_csv('../Data/Joined/Integration/GameKeys/Keys_All_Games_Integrated.csv', index_col=0)

    # join games_mechanic_relation table to replace bga_game_id column with game_keys column:
    mechanics_bgg_games_relation_df = pd.merge(left=mechanics_bgg_games_relation_df, right=game_keys,
                                               left_on='bgg_game_id', right_on='bgg_game_id')

    # replace 'mechanic_name' with 'bgg_mechanic_key' in mechanics_bgg_games_relation:
    mechanics_bgg_games_relation_df = pd.merge(left=mechanics_bgg_games_relation_df, right=mechanics_bgg,
                                               left_on='mechanic_name', right_on='mechanic_name')

    # normalize by only keeping game_key and mechanic_id
    mechanics_bgg_games_relation_df = mechanics_bgg_games_relation_df[['game_key', 'bgg_mechanic_key']]

    # export bgg mechanics:
    export_path = '../Data/BoardGameGeeks/Raw/BGG_Mechanics.csv'
    export_df_to_csv(mechanics_bgg, export_path)

    # export bgg game_mechanics_relation:
    export_path = '../Data/BoardGameGeeks/Processed/GameInformation/04_BGA_Game_Mechanics_Relation_Cleaned.csv'
    export_df_to_csv(mechanics_bgg_games_relation_df, export_path)


def match_and_merge_bga_and_bgg_mechanics():
    # import bga and bgg mechanics
    bga_mechanics = pd.read_csv('../Data/BoardGameAtlas/Raw/API/Mechanics/all_bga_mechanics.csv', index_col=0)
    bgg_mechanics = pd.read_csv('../Data/BoardGameGeeks/Raw/BGG_Mechanics.csv', index_col=0)

    bga_mechanics_names = bga_mechanics['mechanic_name'].tolist()
    bgg_mechanics_names = bgg_mechanics['mechanic_name'].tolist()

    mechanic_jaccard_threshold = 0.5

    # match mechanics:
    mecha_list = []
    for bga_mechanic in bga_mechanics_names:
        match = find_closest_match(bga_mechanic, bgg_mechanics_names, mechanic_jaccard_threshold)
        mecha_list.append(
            {'bga_name': bga_mechanic, 'bgg_name': match['name'], 'jaccard_score': match['jaccard_score']})

    matches_df = pd.DataFrame(mecha_list)

    # drop entries that could not be matched
    matches_df = matches_df[matches_df['jaccard_score'] != ''].sort_values('jaccard_score', ascending=False)

    bga_names_matched = matches_df['bga_name'].tolist()
    bgg_names_matched = matches_df['bgg_name'].tolist()

    # build subsets depending on if mechanic name was matched or not
    bga_subset_matches = bga_mechanics[bga_mechanics['mechanic_name'].isin(bga_names_matched)]
    bgg_subset_matches = bgg_mechanics[bgg_mechanics['mechanic_name'].isin(bgg_names_matched)]

    bga_subset_no_matches = bga_mechanics[~bga_mechanics['mechanic_name'].isin(bga_names_matched)]
    bgg_subset_no_matches = bgg_mechanics[~bgg_mechanics['mechanic_name'].isin(bgg_names_matched)]

    # rename mechanic_name column:
    bga_subset_matches.rename(columns={'mechanic_name': 'bga_name'}, inplace=True)
    bgg_subset_matches.rename(columns={'mechanic_name': 'bgg_name'}, inplace=True)
    bga_subset_no_matches.rename(columns={'mechanic_name': 'bga_name'}, inplace=True)
    bgg_subset_no_matches.rename(columns={'mechanic_name': 'bgg_name'}, inplace=True)

    # join matches:
    # start with bga subset
    subset_matches = pd.merge(left=bga_subset_matches, right=matches_df,
                              left_on='bga_name', right_on='bga_name')
    # and then also merge with the bgg subset
    subset_matches = pd.merge(left=subset_matches, right=bgg_subset_matches,
                              left_on='bgg_name', right_on='bgg_name')
    # keep only relevant columns:
    subset_matches = subset_matches[['mechanic_bga_id', 'bgg_mechanic_key', 'bga_name', 'bgg_name', 'mechanic_bga_url']]

    # concat all:
    all_mechanics = pd.concat([subset_matches, bga_subset_no_matches, bgg_subset_no_matches],
                              ignore_index=True, sort=False).sort_values(['bga_name'])

    # create mechanic key:
    all_mechanics.insert(0, 'mechanic_key', range(1, 1 + len(all_mechanics)))

    # add mechanic_name column:
    # out of the matched mechanics we keep the bgg names:
    all_mechanics['mechanic_name'] = all_mechanics['bgg_name']
    # if it is a bga mechanic that could not be matched, take bga name instead:
    all_mechanics.loc[all_mechanics['mechanic_name'].isna(), 'mechanic_name'] = all_mechanics['bga_name']

    # export mechanics df:
    export_path = '../Data/Joined/Integration/GameInformation/04_Mechanics_Integrated_with_bga_and_bgg_ids.csv'
    export_df_to_csv(all_mechanics, export_path)


def replace_old_ids_with_new_key_and_concatenate_mechanic_relation_tables():
    # import bga_mechanic_game_relations:
    path_1 = '../Data/BoardGameAtlas/Processed/API/04_BGA_Game_Mechanics_Relation_Cleaned.csv'
    bga_mechanics_game_relation = pd.read_csv(path_1, index_col=0)

    # import bgg_mechanic_game_relations:
    path_2 = '../Data/BoardGameGeeks/Processed/GameInformation/04_BGA_Game_Mechanics_Relation_Cleaned.csv'
    bgg_mechanics_game_relation = pd.read_csv(path_2, index_col=0)

    # import mechanics:
    path_3 = '../Data/Joined/Integration/GameInformation/04_Mechanics_Integrated_with_bga_and_bgg_ids.csv'
    mechanics_df = pd.read_csv(path_3, index_col=0)

    # replace old ids in bga_mechanic_game_relations:
    bga_mechanics_game_relation = pd.merge(left=bga_mechanics_game_relation, right=mechanics_df,
                                           left_on='mechanic_id', right_on='mechanic_bga_id')
    bga_mechanics_game_relation = bga_mechanics_game_relation[['game_key', 'mechanic_key']]

    # replace old ids in bgg_mechanic_game_relations:
    bgg_mechanics_game_relation = pd.merge(left=bgg_mechanics_game_relation, right=mechanics_df,
                                           left_on='bgg_mechanic_key', right_on='bgg_mechanic_key')
    bgg_mechanics_game_relation = bgg_mechanics_game_relation[['game_key', 'mechanic_key']]

    # delete old bga and bgg id & name columns in mechanics_df
    mechanics_df = mechanics_df[['mechanic_key', 'mechanic_name', 'mechanic_bga_url']].reset_index(drop=True)


    #
    # CONCATENATE both tables:
    #

    concat_mechanics_game_relation = pd.concat([bga_mechanics_game_relation, bgg_mechanics_game_relation],
                                               ignore_index=True, sort=False).sort_values(['game_key']).reset_index(drop=True)

    # export mechanics_game_relation
    export_path_1 = '../Data/Joined/Integration/GameInformation/4b_Mechanics_Game_Relation_Integrated_and_Normalized.csv'
    export_df_to_csv(concat_mechanics_game_relation, export_path_1)

    # export mechanics_df
    export_path_2 = '../Data/Joined/Integration/GameInformation/04_Mechanics_Integrated_and_Normalized.csv'
    export_df_to_csv(mechanics_df, export_path_2)


def normalize_bga_game_categories_relation():
    # import bga_games_category_relation:
    categories_bga_games_relation_path_fuzzy = '../Data/BoardGameAtlas/Processed/API/05_BGA_Game_Categories_Relation_*.json'
    categories_bga_games_relation_path = get_latest_version_of_file(categories_bga_games_relation_path_fuzzy)
    categories_bga_games_relation_df = import_json_to_dataframe(categories_bga_games_relation_path)

    # import bga categories:
    categories_bga = pd.read_csv('../Data/BoardGameAtlas/Raw/API/categories/all_bga_categories.csv', index_col=0)

    # import game keys:
    game_keys = pd.read_csv('../Data/Joined/Integration/GameKeys/Keys_All_Games_Integrated.csv', index_col=0)

    # join games_category_relation table to replace bga_game_id column with game_keys column:
    categories_bga_games_relation_df = pd.merge(left=categories_bga_games_relation_df, right=game_keys,
                                                left_on='game_id', right_on='bga_game_id')

    # normalize by only keeping game_key and category_id
    categories_bga_games_relation_df = categories_bga_games_relation_df[['game_key', 'category_id']]

    # export df
    export_path = '../Data/BoardGameAtlas/Processed/API/05_BGA_Game_Categories_Relation_Cleaned.csv'
    export_df_to_csv(categories_bga_games_relation_df, export_path)


def normalize_bgg_game_categories_relation():
    # import bgg games:
    categories_bgg_games_relation_path_fuzzy = '../Data/BoardGameGeeks/Processed/GameInformation/05_BGG_Game_category_Relation_*.csv'
    categories_bgg_games_relation_path = get_latest_version_of_file(categories_bgg_games_relation_path_fuzzy)
    categories_bgg_games_relation_df = pd.read_csv(categories_bgg_games_relation_path, index_col=0)

    # create categories list:
    categories_bgg = pd.DataFrame(categories_bgg_games_relation_df['category_name'].drop_duplicates())

    # create temporary key_column:
    categories_bgg.insert(0, 'bgg_category_key', range(1001, 1001 + len(categories_bgg)))

    # import game keys:
    game_keys = pd.read_csv('../Data/Joined/Integration/GameKeys/Keys_All_Games_Integrated.csv', index_col=0)

    # join games_category_relation table to replace bga_game_id column with game_keys column:
    categories_bgg_games_relation_df = pd.merge(left=categories_bgg_games_relation_df, right=game_keys,
                                               left_on='bgg_game_id', right_on='bgg_game_id')

    # replace 'category_name' with 'bgg_category_key' in categories_bgg_games_relation:
    categories_bgg_games_relation_df = pd.merge(left=categories_bgg_games_relation_df, right=categories_bgg,
                                               left_on='category_name', right_on='category_name')

    # normalize by only keeping game_key and category_id
    categories_bgg_games_relation_df = categories_bgg_games_relation_df[['game_key', 'bgg_category_key']]

    # export bgg categories:
    export_path = '../Data/BoardGameGeeks/Raw/BGG_categories.csv'
    export_df_to_csv(categories_bgg, export_path)

    # export bgg game_categories_relation:
    export_path = '../Data/BoardGameGeeks/Processed/GameInformation/05_BGA_Game_Categories_Relation_Cleaned.csv'
    export_df_to_csv(categories_bgg_games_relation_df, export_path)


def match_and_merge_bga_and_bgg_categories():
    # import bga and bgg categories
    bga_categories = pd.read_csv('../Data/BoardGameAtlas/Raw/API/categories/all_bga_categories.csv', index_col=0)
    bgg_categories = pd.read_csv('../Data/BoardGameGeeks/Raw/BGG_categories.csv', index_col=0)

    bga_categories_names = bga_categories['category_name'].tolist()
    bgg_categories_names = bgg_categories['category_name'].tolist()

    category_jaccard_threshold = 0.4

    # match categories:
    mecha_list = []
    for bga_category in bga_categories_names:
        match = find_closest_match(bga_category, bgg_categories_names, category_jaccard_threshold)
        mecha_list.append(
            {'bga_name': bga_category, 'bgg_name': match['name'], 'jaccard_score': match['jaccard_score']})

    matches_df = pd.DataFrame(mecha_list)

    # drop entries that could not be matched
    matches_df = matches_df[matches_df['jaccard_score'] != ''].sort_values('jaccard_score', ascending=False)

    bga_names_matched = matches_df['bga_name'].tolist()
    bgg_names_matched = matches_df['bgg_name'].tolist()

    # build subsets depending on if category name was matched or not
    bga_subset_matches = bga_categories[bga_categories['category_name'].isin(bga_names_matched)]
    bgg_subset_matches = bgg_categories[bgg_categories['category_name'].isin(bgg_names_matched)]

    bga_subset_no_matches = bga_categories[~bga_categories['category_name'].isin(bga_names_matched)]
    bgg_subset_no_matches = bgg_categories[~bgg_categories['category_name'].isin(bgg_names_matched)]

    # rename category_name column:
    bga_subset_matches.rename(columns={'category_name': 'bga_name'}, inplace=True)
    bgg_subset_matches.rename(columns={'category_name': 'bgg_name'}, inplace=True)
    bga_subset_no_matches.rename(columns={'category_name': 'bga_name'}, inplace=True)
    bgg_subset_no_matches.rename(columns={'category_name': 'bgg_name'}, inplace=True)

    # join matches:
    # start with bga subset
    subset_matches = pd.merge(left=bga_subset_matches, right=matches_df,
                              left_on='bga_name', right_on='bga_name')
    # and then also merge with the bgg subset
    subset_matches = pd.merge(left=subset_matches, right=bgg_subset_matches,
                              left_on='bgg_name', right_on='bgg_name')
    # keep only relevant columns:
    subset_matches = subset_matches[['category_bga_id', 'bgg_category_key', 'bga_name', 'bgg_name', 'category_bga_url']]

    # concat all:
    all_categories = pd.concat([subset_matches, bga_subset_no_matches, bgg_subset_no_matches],
                              ignore_index=True, sort=False).sort_values(['bga_name'])

    # create category key:
    all_categories.insert(0, 'category_key', range(1, 1 + len(all_categories)))

    # add category_name column:
    # out of the matched categories we keep the bgg names:
    all_categories['category_name'] = all_categories['bgg_name']
    # if it is a bga category that could not be matched, take bga name instead:
    all_categories.loc[all_categories['category_name'].isna(), 'category_name'] = all_categories['bga_name']

    # export categories df:
    export_path = '../Data/Joined/Integration/GameInformation/05_Categories_Integrated_with_bga_and_bgg_ids.csv'
    export_df_to_csv(all_categories, export_path)


def replace_old_ids_with_new_key_and_concatenate_category_relation_tables():
    # import bga_category_game_relations:
    path_1 = '../Data/BoardGameAtlas/Processed/API/05_BGA_Game_Categories_Relation_Cleaned.csv'
    bga_categories_game_relation = pd.read_csv(path_1, index_col=0)

    # import bgg_category_game_relations:
    path_2 = '../Data/BoardGameGeeks/Processed/GameInformation/05_BGA_Game_Categories_Relation_Cleaned.csv'
    bgg_categories_game_relation = pd.read_csv(path_2, index_col=0)

    # import categories:
    path_3 = '../Data/Joined/Integration/GameInformation/05_categories_Integrated_with_bga_and_bgg_ids.csv'
    categories_df = pd.read_csv(path_3, index_col=0)

    # replace old ids in bga_category_game_relations:
    bga_categories_game_relation = pd.merge(left=bga_categories_game_relation, right=categories_df,
                                           left_on='category_id', right_on='category_bga_id')
    bga_categories_game_relation = bga_categories_game_relation[['game_key', 'category_key']]

    # replace old ids in bgg_category_game_relations:
    bgg_categories_game_relation = pd.merge(left=bgg_categories_game_relation, right=categories_df,
                                           left_on='bgg_category_key', right_on='bgg_category_key')
    bgg_categories_game_relation = bgg_categories_game_relation[['game_key', 'category_key']]

    # delete old bga and bgg id & name columns in categories_df
    categories_df = categories_df[['category_key', 'category_name', 'category_bga_url']].reset_index(drop=True)


    #
    # CONCATENATE both tables:
    #

    concat_categories_game_relation = pd.concat([bga_categories_game_relation, bgg_categories_game_relation],
                                                ignore_index=True, sort=False).sort_values(['game_key']).reset_index(drop=True)

    # export categories_game_relation
    export_path_1 = '../Data/Joined/Integration/GameInformation/5b_categories_Game_Relation_Integrated_and_Normalized.csv'
    export_df_to_csv(concat_categories_game_relation, export_path_1)

    # export categories_df
    export_path_2 = '../Data/Joined/Integration/GameInformation/05_categories_Integrated_and_Normalized.csv'
    export_df_to_csv(categories_df, export_path_2)



def create_list_of_all_bga_publishers():
    # import bga publishers
    fuzzy_import_path_1 = '../Data/BoardGameAtlas/Processed/API/02_BGA_Game_Publishers_Relation*.json'
    import_path_1 = get_latest_version_of_file(fuzzy_import_path_1)
    bga_publishers_game_relation = import_json_to_dataframe(import_path_1)

    # extract publishers ids and publisher urls
    publishers = bga_publishers_game_relation[['publisher_id', 'publisher_url']]

    # keep only unique publishers:
    publishers.drop_duplicates(subset='publisher_id', keep='first', inplace=True)

    # export publishers to csv:
    export_path = '../Data/BoardGameAtlas/Processed/API/BGA_All_Unique_Publishers.csv'
    export_df_to_csv(publishers, export_path)


