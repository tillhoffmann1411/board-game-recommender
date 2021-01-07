import pandas as pd
import numpy as np
import os
import json
import glob
from datetime import datetime

from ETL.Integration.bgg_and_bga_integration import find_closest_match
from ETL.helper import import_json_to_dataframe, export_df_to_json, export_df_to_csv, \
    get_latest_version_of_file, get_bga_publishers


JACCARD_THRESHOLD_PUBLISHERS = 0.6
JACCARD_THRESHOLD_DESIGNERS = 0.55


def integrate_auxiliary_tables():
    # 1) Publishers
    integrate_publishers()

    # 2) Designers
    integrate_designers()

    # 3) Mechanics
    integrate_mechanics()

    # 4) Categories
    integrate_categories()

    # 5) Names
    integrate_game_name_translations()


def integrate_publishers():
    # 1) create a list of all unique bga publishers, including their id and the bga publisher url
    create_list_of_all_bga_publishers()

    # 2) scrape publisher data from bga [this is done in a separate python project due to unexpected issues with
    #    scrapy and therefore not called here]

    # 3) merge scraped publisher data with publisher data retrieved from api:
    merge_scraped_bga_publisher_data_and_api_data()

    # 4) create publisher table by merging bga and bgg publishers
    merge_bga_and_bgg_publishers()

    # 5) merge bga and bgg publisher_game_relation tables
    merge_bga_and_bgg_publisher_game_relation()


def integrate_designers():
    # 1) create a list of all unique bga publishers, including their id and the bga publisher url
    create_list_of_all_bga_designers()

    # 2) scrape designer data from bga [this is done in a separate python project due to unexpected issues with
    #    scrapy and therefore not called here]

    # 3) merge scraped designer data with designer data retrieved from api:
    merge_scraped_bga_designer_data_and_api_data()

    # 4) create designer table by merging bga and bgg designers
    merge_bga_and_bgg_designers()

    # 5) merge bga and bgg designer_game_relation tables
    merge_bga_and_bgg_designer_game_relation()


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


def integrate_game_name_translations():
    # Integrate the game_name_relations tables of both bga and bgg:
    integrate_game_name_relation_tables()


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
                                               ignore_index=True, sort=False).sort_values(['game_key']).reset_index(
        drop=True)

    # export mechanics_game_relation
    export_path_1 = '../Data/Joined/Results/Mechanic_Game_Relation.csv'
    export_df_to_csv(concat_mechanics_game_relation, export_path_1)

    # export mechanics_df
    export_path_2 = '../Data/Joined/Results/Mechanics.csv'
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
                                                ignore_index=True, sort=False).sort_values(['game_key']).reset_index(
        drop=True)

    # export categories_game_relation
    export_path_1 = '../Data/Joined/Results/Category_Game_Relation.csv'
    export_df_to_csv(concat_categories_game_relation, export_path_1)

    # export categories_df
    export_path_2 = '../Data/Joined/Results/Categories.csv'
    export_df_to_csv(categories_df, export_path_2)


def create_list_of_all_bga_publishers():
    # import bga publishers
    fuzzy_import_path = '../Data/BoardGameAtlas/Processed/API/02_BGA_Game_Publishers_Relation*.json'
    import_path_1 = get_latest_version_of_file(fuzzy_import_path)
    bga_publishers_game_relation = import_json_to_dataframe(import_path_1)

    # extract publishers ids and publisher urls
    publishers = bga_publishers_game_relation[['publisher_id', 'publisher_url']]

    # keep only unique publishers:
    publishers.drop_duplicates(subset='publisher_id', keep='first', inplace=True)

    # export publishers to csv:
    export_path = '../Data/BoardGameAtlas/Processed/API/BGA_All_Unique_Publishers.csv'
    export_df_to_csv(publishers, export_path)


def merge_scraped_bga_publisher_data_and_api_data():
    # import scraped bga publisher data
    import_path_1 = '../Data/BoardGameAtlas/Raw/Scrapy/Publishers/bga_publishers.json'
    publishers_scrapy = import_json_to_dataframe(import_path_1)

    # import api bga publisher data
    import_path_2_fuzzy = '../Data/BoardGameAtlas/Processed/API/02_BGA_Game_Publishers_Relation_*.json'
    import_path_2 = get_latest_version_of_file(import_path_2_fuzzy)
    publishers_game_relation = import_json_to_dataframe(import_path_2)

    # remove list around publisher url:
    publishers_scrapy = publishers_scrapy.explode('publisher_bga_image_url')

    # merge both dataframes:
    publishers_merged = pd.merge(left=publishers_scrapy, right=publishers_game_relation,
                                 left_on='publisher_url', right_on='publisher_url')

    # export df
    export_path = '../Data/BoardGameAtlas/Processed/API/bga_publishers_scrapy_and_api_data_merged.csv'
    export_df_to_csv(publishers_merged, export_path)


def merge_bga_and_bgg_publishers():
    # import bga data:
    import_path_1 = '../Data/BoardGameAtlas/Processed/API/bga_publishers_scrapy_and_api_data_merged.csv'
    bga_publishers_game_relation = pd.read_csv(import_path_1, index_col=0)

    # import bgg data:
    import_path_2_fuzzy = '../Data/BoardGameGeeks/Processed/GameInformation/02_BGG_Game_Publisher_Relation_*.csv'
    import_path_2 = get_latest_version_of_file(import_path_2_fuzzy)
    bgg_publishers_game_relation = pd.read_csv(import_path_2, index_col=0)

    # create publishers df:
    bga_publishers_df = bga_publishers_game_relation[['publisher_name', 'publisher_bga_image_url', 'publisher_url', 'publisher_id']].drop_duplicates()
    bga_publishers_df.rename(columns={'publisher_bga_image_url': 'publisher_image_url', 'publisher_id': 'publisher_bga_id'}, inplace=True)

    bgg_publishers_df = pd.DataFrame(bgg_publishers_game_relation[['publisher_name']].drop_duplicates())
    bgg_publishers_df.rename(columns={'publisher_name': 'bgg_publisher_name'}, inplace=True)

    # add bgg_publisher_key:
    bgg_publishers_df.insert(0, 'publisher_bgg_key', range(1, 1 + len(bgg_publishers_df)))

    # extract publisher names:
    bga_publisher_names_list = bga_publishers_game_relation['publisher_name'].drop_duplicates().to_list()
    bgg_publisher_names_list = bgg_publishers_game_relation['publisher_name'].drop_duplicates().to_list()

    # match publisher names:
    # get exact name matches:
    exact_matches = list(set(bga_publisher_names_list).intersection(bgg_publisher_names_list))

    # subsets for data that could not get matched exactly:
    bga_names_not_matched_list = [name for name in bga_publisher_names_list if name not in exact_matches]
    bgg_names_not_matched_list = [name for name in bgg_publisher_names_list if name not in exact_matches]

    # jaccard matching for names that could not be matched exactly
    matches = []
    for bga_publisher in bga_names_not_matched_list:
        match = find_closest_match(bga_publisher, bgg_names_not_matched_list, JACCARD_THRESHOLD_PUBLISHERS)
        matches.append(
            {'bga_name': bga_publisher, 'bgg_name': match['name'], 'jaccard_score': match['jaccard_score']})

    # create list of matched publisher names:
    jaccard_matches_bga = [publisher['bga_name'] for publisher in matches if publisher['jaccard_score'] != '']
    jaccard_matches_bgg = [publisher['bgg_name'] for publisher in matches if publisher['jaccard_score'] != '']

    # create list of a games matched:
    all_matches_bga = exact_matches + jaccard_matches_bga
    all_matches_bgg = exact_matches + jaccard_matches_bgg

    # create dataframe of matched publishers:
    jaccard_matches_df = pd.DataFrame(matches)
    jaccard_matches_df = jaccard_matches_df[jaccard_matches_df['jaccard_score'] != ''].sort_values('jaccard_score', ascending=False)
    del jaccard_matches_df['jaccard_score']

    # 1) Create DF of all publishers that could be matched
    #       a) exact matches
    #       b) jaccard matches
    # 2) Create DF of bga publishers that could not be matched
    # 3) Create DF ob bgg publishers that could not be matched
    # 4) Concat all DFs to one publishers df

    # Structure: publisher_key | publisher_name | publisher_bga_id | publisher_bgg_id | publisher_url | publisher_image_url
    # 1) a)
    bga_exact_matches = bga_publishers_df[bga_publishers_df['publisher_name'].isin(exact_matches)]
    bgg_exact_matches = bgg_publishers_df[bgg_publishers_df['bgg_publisher_name'].isin(exact_matches)]

    joined_exact_matches = pd.merge(left=bga_exact_matches, right=bgg_exact_matches,
                                    left_on='publisher_name', right_on='bgg_publisher_name')

    # 1) b)
    bga_jaccard_matches = pd.merge(left=bga_publishers_df, right=jaccard_matches_df, left_on='publisher_name', right_on='bga_name')
    bgg_jaccard_matches = pd.merge(left=bgg_publishers_df, right=jaccard_matches_df, left_on='bgg_publisher_name', right_on='bgg_name')

    joined_jaccard_matches = pd.merge(left=bga_jaccard_matches, right=bgg_jaccard_matches,
                                      left_on='publisher_name', right_on='bga_name')
    # drop columns not needed
    joined_jaccard_matches = joined_jaccard_matches[['publisher_name', 'publisher_bga_id', 'publisher_bgg_key', 'bgg_publisher_name', 'publisher_url', 'publisher_image_url']]


    # 2)
    bga_no_matches = bga_publishers_df[~bga_publishers_df['publisher_name'].isin(all_matches_bga)]

    # 3)
    bgg_no_matches = bgg_publishers_df[~bgg_publishers_df['bgg_publisher_name'].isin(all_matches_bgg)]

    # 4) Create large dataframe by concatenating all dataframes:
    # size: 473 [1a] + 7 [1b] + 25 [2] + 5928 [3] = 6433
    publishers_df = pd.concat([joined_exact_matches, joined_jaccard_matches, bga_no_matches, bgg_no_matches])

    # add publisher key:
    publishers_df.insert(0, 'publisher_key', range(1, 1 + len(publishers_df)))

    # export publishers
    export_path = '../Data/Joined/Results/Publisher.csv'
    export_df_to_csv(publishers_df, export_path)


def merge_bga_and_bgg_publisher_game_relation():
    # import bga_publisher_game_relation
    import_path_1 = '../Data/BoardGameAtlas/Processed/API/bga_publishers_scrapy_and_api_data_merged.csv'
    game_publisher_relation_bga = pd.read_csv(import_path_1, index_col=0)
    game_publisher_relation_bga = game_publisher_relation_bga[['game_id', 'publisher_id']]

    # import bgg_publisher_game_relation
    import_path_2_fuzzy = '../Data/BoardGameGeeks/Processed/GameInformation/02_BGG_Game_Publisher_Relation_*.csv'
    import_path_2 = get_latest_version_of_file(import_path_2_fuzzy)
    game_publisher_relation_bgg = pd.read_csv(import_path_2, index_col=0)
    game_publisher_relation_bgg = game_publisher_relation_bgg[['bgg_game_id', 'publisher_name']]

    # import publishers
    import_path_3 = '../Data/Joined/Results/Publisher.csv'
    publishers = pd.read_csv(import_path_3, index_col=0)

    # import game keys
    import_path_4 = '../Data/Joined/Integration/GameKeys/Keys_All_Games_Integrated.csv'
    game_keys = pd.read_csv(import_path_4, index_col=0)


    # replace bga game ids with game keys
    game_publisher_relation_bga = pd.merge(left=game_publisher_relation_bga, right=game_keys,
                                           left_on='game_id', right_on='bga_game_id')
    game_publisher_relation_bga = game_publisher_relation_bga[['game_key', 'publisher_id']]

    # replace publisher_bga_id with publisher_key
    game_publisher_relation_bga = pd.merge(left=publishers, right=game_publisher_relation_bga,
                                           left_on='publisher_bga_id', right_on='publisher_id')
    game_publisher_relation_bga = game_publisher_relation_bga[['game_key', 'publisher_key']]


    # replace bgg game ids with game keys
    game_publisher_relation_bgg = pd.merge(left=game_publisher_relation_bgg, right=game_keys,
                                           left_on='bgg_game_id', right_on='bgg_game_id')
    game_publisher_relation_bgg = game_publisher_relation_bgg[['game_key', 'publisher_name']]

    # replace bgg publisher name with publisher key
    game_publisher_relation_bgg = pd.merge(left=game_publisher_relation_bgg, right=publishers,
                                           left_on='publisher_name', right_on='bgg_publisher_name')
    game_publisher_relation_bgg = game_publisher_relation_bgg[['game_key', 'publisher_key']]


    # concat both dataframes:
    game_publisher_relation_combined = pd.concat([game_publisher_relation_bga, game_publisher_relation_bgg])

    # export game_publisher relation:
    export_path = '../Data/Joined/Results/Publisher_Game_Relation.csv'
    export_df_to_csv(game_publisher_relation_combined, export_path)


def create_list_of_all_bga_designers():
    # import bga designers
    fuzzy_import_path = '../Data/BoardGameAtlas/Processed/API/03_BGA_Game_designers_Relation*.json'
    import_path = get_latest_version_of_file(fuzzy_import_path)
    bga_designers_game_relation = import_json_to_dataframe(import_path)

    # extract designers ids and designer urls
    designers = bga_designers_game_relation[['designer_id', 'designer_url']]

    # keep only unique designers:
    designers.drop_duplicates(subset='designer_id', keep='first', inplace=True)

    # export designers to csv:
    export_path = '../Data/BoardGameAtlas/Processed/API/BGA_All_Unique_designers.csv'
    export_df_to_csv(designers, export_path)


def merge_scraped_bga_designer_data_and_api_data():
    # import scraped bga designer data
    import_path_1 = '../Data/BoardGameAtlas/Raw/Scrapy/designers/bga_designers.json'
    designers_scrapy = import_json_to_dataframe(import_path_1)

    # import api bga designer data
    import_path_2_fuzzy = '../Data/BoardGameAtlas/Processed/API/03_BGA_Game_designers_Relation_*.json'
    import_path_2 = get_latest_version_of_file(import_path_2_fuzzy)
    designers_game_relation = import_json_to_dataframe(import_path_2)

    # remove list around designer url:
    designers_scrapy = designers_scrapy.explode('designer_bga_image_url')

    # merge both dataframes:
    designers_merged = pd.merge(left=designers_scrapy, right=designers_game_relation,
                                left_on='designer_url', right_on='designer_url')

    # export df
    export_path = '../Data/BoardGameAtlas/Processed/API/bga_designers_scrapy_and_api_data_merged.csv'
    export_df_to_csv(designers_merged, export_path)


def merge_bga_and_bgg_designers():
    # import bga data:
    import_path_1 = '../Data/BoardGameAtlas/Processed/API/bga_designers_scrapy_and_api_data_merged.csv'
    bga_designers_game_relation = pd.read_csv(import_path_1, index_col=0)

    # import bgg data:
    import_path_2_fuzzy = '../Data/BoardGameGeeks/Processed/GameInformation/03_BGG_Game_designer_Relation_*.csv'
    import_path_2 = get_latest_version_of_file(import_path_2_fuzzy)
    bgg_designers_game_relation = pd.read_csv(import_path_2, index_col=0)

    # drop NA's from bga_designers_game_relation names
    bga_designers_na = bga_designers_game_relation[bga_designers_game_relation['designer_name'].isnull()]
    if len(bga_designers_na) > 0:
        print(str(len(bga_designers_na))+ ' rows dropped from bga_game_relation table because designer_names are missing.')
        bga_designers_game_relation = bga_designers_game_relation[~bga_designers_game_relation['designer_name'].isnull()]


    # create designers df:
    bga_designers_df = bga_designers_game_relation[['designer_name', 'designer_bga_image_url', 'designer_url', 'designer_id']].drop_duplicates()
    bga_designers_df.rename(columns={'designer_bga_image_url': 'designer_image_url', 'designer_id': 'designer_bga_id'}, inplace=True)

    bgg_designers_df = pd.DataFrame(bgg_designers_game_relation[['designer_name']].drop_duplicates())
    bgg_designers_df.rename(columns={'designer_name': 'bgg_designer_name'}, inplace=True)

    # add bgg_designer_key:
    bgg_designers_df.insert(0, 'designer_bgg_key', range(1, 1 + len(bgg_designers_df)))

    # extract designer names:
    bga_designer_names_list = bga_designers_game_relation['designer_name'].drop_duplicates().to_list()
    bgg_designer_names_list = bgg_designers_game_relation['designer_name'].drop_duplicates().to_list()

    # match designer names:
    # get exact name matches:
    exact_matches = list(set(bga_designer_names_list).intersection(bgg_designer_names_list))

    # subsets for data that could not get matched exactly:
    bga_names_not_matched_list = [name for name in bga_designer_names_list if name not in exact_matches]
    bgg_names_not_matched_list = [name for name in bgg_designer_names_list if name not in exact_matches]

    # jaccard matching for names that could not be matched exactly
    matches = []
    for bga_designer in bga_names_not_matched_list:
        match = find_closest_match(bga_designer, bgg_names_not_matched_list, JACCARD_THRESHOLD_DESIGNERS)
        matches.append(
            {'bga_name': bga_designer, 'bgg_name': match['name'], 'jaccard_score': match['jaccard_score']})

    # create list of matched designer names:
    jaccard_matches_bga = [designer['bga_name'] for designer in matches if designer['jaccard_score'] != '']
    jaccard_matches_bgg = [designer['bgg_name'] for designer in matches if designer['jaccard_score'] != '']

    # create list of a games matched:
    all_matches_bga = exact_matches + jaccard_matches_bga
    all_matches_bgg = exact_matches + jaccard_matches_bgg

    # create dataframe of matched designers:
    jaccard_matches_df = pd.DataFrame(matches)
    jaccard_matches_df = jaccard_matches_df[jaccard_matches_df['jaccard_score'] != ''].sort_values('jaccard_score', ascending=False)
    del jaccard_matches_df['jaccard_score']

    # 1) Create DF of all designers that could be matched
    #       a) exact matches
    #       b) jaccard matches
    # 2) Create DF of bga designers that could not be matched
    # 3) Create DF ob bgg designers that could not be matched
    # 4) Concat all DFs to one designers df

    # Structure: designer_key | designer_name | designer_bga_id | designer_bgg_id | designer_url | designer_image_url
    # 1) a)
    bga_exact_matches = bga_designers_df[bga_designers_df['designer_name'].isin(exact_matches)]
    bgg_exact_matches = bgg_designers_df[bgg_designers_df['bgg_designer_name'].isin(exact_matches)]

    joined_exact_matches = pd.merge(left=bga_exact_matches, right=bgg_exact_matches,
                                    left_on='designer_name', right_on='bgg_designer_name')

    # 1) b)
    bga_jaccard_matches = pd.merge(left=bga_designers_df, right=jaccard_matches_df, left_on='designer_name', right_on='bga_name')
    bgg_jaccard_matches = pd.merge(left=bgg_designers_df, right=jaccard_matches_df, left_on='bgg_designer_name', right_on='bgg_name')

    joined_jaccard_matches = pd.merge(left=bga_jaccard_matches, right=bgg_jaccard_matches,
                                      left_on='designer_name', right_on='bga_name')
    # drop columns not needed
    joined_jaccard_matches = joined_jaccard_matches[['designer_name', 'designer_bga_id', 'designer_bgg_key', 'bgg_designer_name', 'designer_url', 'designer_image_url']]


    # 2)
    bga_no_matches = bga_designers_df[~bga_designers_df['designer_name'].isin(all_matches_bga)]

    # 3)
    bgg_no_matches = bgg_designers_df[~bgg_designers_df['bgg_designer_name'].isin(all_matches_bgg)]

    # 4) Create large dataframe by concatenating all dataframes:
    # size: 473 [1a] + 7 [1b] + 25 [2] + 5928 [3] = 6433
    designers_df = pd.concat([joined_exact_matches, joined_jaccard_matches, bga_no_matches, bgg_no_matches])

    # add designer key:
    designers_df.insert(0, 'designer_key', range(1, 1 + len(designers_df)))

    # export designers
    export_path = '../Data/Joined/Results/Designer.csv'
    export_df_to_csv(designers_df, export_path)



def merge_bga_and_bgg_publisher_game_relation():
    # import bga_publisher_game_relation
    import_path_1 = '../Data/BoardGameAtlas/Processed/API/bga_publishers_scrapy_and_api_data_merged.csv'
    game_publisher_relation_bga = pd.read_csv(import_path_1, index_col=0)
    game_publisher_relation_bga = game_publisher_relation_bga[['game_id', 'publisher_id']]

    # import bgg_publisher_game_relation
    import_path_2_fuzzy = '../Data/BoardGameGeeks/Processed/GameInformation/02_BGG_Game_Publisher_Relation_*.csv'
    import_path_2 = get_latest_version_of_file(import_path_2_fuzzy)
    game_publisher_relation_bgg = pd.read_csv(import_path_2, index_col=0)
    game_publisher_relation_bgg = game_publisher_relation_bgg[['bgg_game_id', 'publisher_name']]

    # import publishers
    import_path_3 = '../Data/Joined/Results/publisher.csv'
    publishers = pd.read_csv(import_path_3, index_col=0)

    # import game keys
    import_path_4 = '../Data/Joined/Integration/GameKeys/Keys_All_Games_Integrated.csv'
    game_keys = pd.read_csv(import_path_4, index_col=0)


    # replace bga game ids with game keys
    game_publisher_relation_bga = pd.merge(left=game_publisher_relation_bga, right=game_keys,
                                           left_on='game_id', right_on='bga_game_id')
    game_publisher_relation_bga = game_publisher_relation_bga[['game_key', 'publisher_id']]

    # replace publisher_bga_id with publisher_key
    game_publisher_relation_bga = pd.merge(left=publishers, right=game_publisher_relation_bga,
                                           left_on='publisher_bga_id', right_on='publisher_id')
    game_publisher_relation_bga = game_publisher_relation_bga[['game_key', 'publisher_key']]


    # replace bgg game ids with game keys
    game_publisher_relation_bgg = pd.merge(left=game_publisher_relation_bgg, right=game_keys,
                                           left_on='bgg_game_id', right_on='bgg_game_id')
    game_publisher_relation_bgg = game_publisher_relation_bgg[['game_key', 'publisher_name']]

    # replace bgg publisher name with publisher key
    game_publisher_relation_bgg = pd.merge(left=game_publisher_relation_bgg, right=publishers,
                                           left_on='publisher_name', right_on='bgg_publisher_name')
    game_publisher_relation_bgg = game_publisher_relation_bgg[['game_key', 'publisher_key']]


    # concat both dataframes:
    game_publisher_relation_combined = pd.concat([game_publisher_relation_bga, game_publisher_relation_bgg])

    # export game_publisher relation:
    export_path = '../Data/Joined/Integration/GameInformation/02b_Publisher_Game_Relation_Integrated'
    export_df_to_csv(game_publisher_relation_combined, export_path)


def create_list_of_all_bga_designers():
    # import bga designers
    fuzzy_import_path = '../Data/BoardGameAtlas/Processed/API/03_BGA_Game_designers_Relation*.json'
    import_path = get_latest_version_of_file(fuzzy_import_path)
    bga_designers_game_relation = import_json_to_dataframe(import_path)

    # extract designers ids and designer urls
    designers = bga_designers_game_relation[['designer_id', 'designer_url']]

    # keep only unique designers:
    designers.drop_duplicates(subset='designer_id', keep='first', inplace=True)

    # export designers to csv:
    export_path = '../Data/BoardGameAtlas/Processed/API/BGA_All_Unique_designers.csv'
    export_df_to_csv(designers, export_path)



def merge_bga_and_bgg_designer_game_relation():
    # import bga_designer_game_relation
    import_path_1 = '../Data/BoardGameAtlas/Processed/API/bga_designers_scrapy_and_api_data_merged.csv'
    game_designer_relation_bga = pd.read_csv(import_path_1, index_col=0)
    game_designer_relation_bga = game_designer_relation_bga[['game_id', 'designer_id']]

    # import bgg_designer_game_relation
    import_path_2_fuzzy = '../Data/BoardGameGeeks/Processed/GameInformation/03_BGG_Game_designer_Relation_*.csv'
    import_path_2 = get_latest_version_of_file(import_path_2_fuzzy)
    game_designer_relation_bgg = pd.read_csv(import_path_2, index_col=0)
    game_designer_relation_bgg = game_designer_relation_bgg[['bgg_game_id', 'designer_name']]

    # import designers
    import_path_3 = '../Data/Joined/Results/Designer.csv'
    designers = pd.read_csv(import_path_3, index_col=0)

    # import game keys
    import_path_4 = '../Data/Joined/Integration/GameKeys/Keys_All_Games_Integrated.csv'
    game_keys = pd.read_csv(import_path_4, index_col=0)


    # replace bga game ids with game keys
    game_designer_relation_bga = pd.merge(left=game_designer_relation_bga, right=game_keys,
                                           left_on='game_id', right_on='bga_game_id')
    game_designer_relation_bga = game_designer_relation_bga[['game_key', 'designer_id']]

    # replace designer_bga_id with designer_key
    game_designer_relation_bga = pd.merge(left=designers, right=game_designer_relation_bga,
                                           left_on='designer_bga_id', right_on='designer_id')
    game_designer_relation_bga = game_designer_relation_bga[['game_key', 'designer_key']]


    # replace bgg game ids with game keys
    game_designer_relation_bgg = pd.merge(left=game_designer_relation_bgg, right=game_keys,
                                           left_on='bgg_game_id', right_on='bgg_game_id')
    game_designer_relation_bgg = game_designer_relation_bgg[['game_key', 'designer_name']]

    # replace bgg designer name with designer key
    game_designer_relation_bgg = pd.merge(left=game_designer_relation_bgg, right=designers,
                                           left_on='designer_name', right_on='bgg_designer_name')
    game_designer_relation_bgg = game_designer_relation_bgg[['game_key', 'designer_key']]


    # concat both dataframes:
    game_designer_relation_combined = pd.concat([game_designer_relation_bga, game_designer_relation_bgg])

    # export game_designer relation:
    export_path = '../Data/Joined/Integration/GameInformation/03b_designer_Game_Relation_Integrated'
    export_df_to_csv(game_designer_relation_combined, export_path)


def integrate_game_name_relation_tables():
    # Import BGA game_name_relation table:
    fuzzy_import_path_1 = '../Data/BoardGameAtlas/Processed/API/06_BGA_Game_Names_Relation_*.json'
    import_path_1 = get_latest_version_of_file(fuzzy_import_path_1)
    names_bga = import_json_to_dataframe(import_path_1)

    # Import BGG game_name_relation table:
    fuzzy_import_path_2 = '../Data/BoardGameGeeks/Processed/GameInformation/06_BGG_Game_Name_Relation_*.csv'
    import_path_2 = get_latest_version_of_file(fuzzy_import_path_2)
    names_bgg = pd.read_csv(import_path_2, index_col=0)

    # Import Game keys:
    import_path_3 = '../Data/Joined/Integration/GameKeys/Keys_All_Games_Integrated.csv'
    game_keys = pd.read_csv(import_path_3, index_col=0)

    # Replace bga 'game_id' with 'game_key'
    names_bga = pd.merge(left=names_bga, right=game_keys, left_on='game_id', right_on='bga_game_id')
    names_bga = names_bga[['game_key', 'game_name']]

    # Replace bgg 'game_id' with 'game_key'
    names_bgg = pd.merge(left=names_bgg, right=game_keys, left_on='bgg_game_id', right_on='bgg_game_id')
    names_bgg = names_bgg[['game_key', 'game_name']]

    # Merge both dataframes:
    names_combined = pd.concat([names_bga, names_bgg]).sort_values('game_key')

    # Remove duplicates:
    print('Number of duplicate game names found and dropped: '+str(len(names_combined)-len(names_combined.drop_duplicates())))
    names_combined.drop_duplicates(inplace=True)

    # Export result:
    export_path = '../Data/Joined/Results/GameNameTranslation.csv'
    export_df_to_csv(names_combined, export_path)
