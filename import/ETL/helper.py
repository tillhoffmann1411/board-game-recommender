import os

import pandas as pd
import json
import glob


def get_bga_ids_of_all_games():
    df = pd.read_json('../Data/BoardGameAtlas/Processed/Scrapy/bga_all_120k_game_ids.json',
                      orient='records', lines=False)
    df = df[['bga_game_id']]

    ids = df['bga_game_id'].tolist()
    return ids


def get_board_game_names_and_ids():
    df = pd.read_json(
        '../Data/BoardGameAtlas/Processed/Scrapy/bga_GameInformation_scrapy_CLEANED.json',
        lines=False)

    df = df[['bga_game_id', 'name']]

    # replace spaces with '-'
    df['name'] = df['name'].str.replace(" ", "-")

    # format to list of dictionaries:
    #     ids = [{'id': 'TAAifFP590', 'name': 'root'},
    #            {'id': '5H5JS0KLzK', 'name': 'wingspan'},
    #            {'id': 'i5Oqu5VZgP', 'name': 'azul'}
    #            ]

    ids = df.to_dict('records')
    return ids


def get_bga_publishers():
    import_path = '../Data/BoardGameAtlas/Processed/API/BGA_All_Unique_Publishers.csv'
    publishers = pd.read_csv(import_path, index_col=0)

    pub_list = publishers.values.tolist()

    return pub_list

def import_bga_boardgames(name_and_location):
    df = pd.read_json(name_and_location, lines=True)
    return df


def export_df_to_json(df, path_and_name):
    df.to_json(path_and_name)
    print("Json file exported to: " + str(path_and_name))


def export_df_to_csv(df, path_and_name):
    df.to_csv(path_and_name)
    print("CSV file exported to: " + str(path_and_name))


def export_dic_to_json(dic, path_and_name):
    with open(path_and_name, 'w') as fp:
        json.dump(dic, fp, sort_keys=False, indent=4)


def import_json_to_dataframe(path_and_filename, orient='records'):
    df = pd.read_json(path_and_filename, orient=orient)
    return df


def get_latest_version_of_file(path_and_filename, num_files=1):
    # since the exact filename is unknown, we have to find the desired file(s) first:
    files = glob.glob('../Data/BoardGameAtlas/Processed/API/01_BGA_Game_Information_*.json')
    files = glob.glob(path_and_filename)

    # sort by date, so that we can get the latest files
    files.sort(key=os.path.getmtime, reverse=True)

    if num_files == 1:
        return files[0]
    else:
        return files[0:min(num_files, len(files))]




