import pandas as pd
import numpy as np
import re

from ETL.helper import import_json_to_dataframe, get_latest_version_of_file, export_df_to_csv

JACCARD_THRESHOLD = 0.31034


def match_game_names():
    bgg_filename = get_latest_version_of_file(
        '../Data/BoardGameGeeks/Processed/GameInformation/01_BGG_Game_Information_*.csv')
    bgg_df = pd.read_csv(bgg_filename, index_col=0)
    bgg_names = bgg_df['name'].tolist()

    bga_filename = get_latest_version_of_file('../Data/BoardGameAtlas/Processed/API/01_BGA_Game_Information_*.json')
    bga_df = import_json_to_dataframe(bga_filename)
    bga_names = bga_df['name'].tolist()

    bgg_ids = bgg_df['bgg_game_id'].tolist()
    bga_ids = bga_df['bga_game_id'].tolist()

    # get duplicate names:
    bgg_duplicate_names = set([x for x in bgg_names if bgg_names.count(x) > 1])
    bga_duplicate_names = set([x for x in bga_names if bga_names.count(x) > 1])

    # find exact matches:
    exact_matches = list(set(bga_names).intersection(bgg_names))

    # subtract exact matches from datasets:
    subset_bgg_df = bgg_df[~bgg_df['name'].isin(exact_matches)]
    subset_bga_df = bga_df[~bga_df['name'].isin(exact_matches)]
    subset_bgg_df.rename(columns={'year_published': 'year_published_bgg'}, inplace=True)
    subset_bga_df.rename(columns={'year_published': 'year_published_bga'}, inplace=True)

    # observation: in almost all cases year_published is the same in both datasets:
    # this helps reducing the amount of names that have to be compared by a lot by grouping by year_published!

    # extract years from bga dataset:
    # a lot of type casting due to unexpected errors with float and set
    all_years = subset_bga_df['year_published_bga'].dropna().tolist()
    all_years = list(map(int, all_years))
    years = list(set(all_years))
    years.sort(reverse=True)

    # drop NA's from name matching:
    print('Dropped ' + str(
        subset_bgg_df['year_published_bgg'].isna().sum()) + ' rows from bga_dataset from name_matching')
    print('Dropped ' + str(
        subset_bga_df['year_published_bga'].isna().sum()) + ' rows from bgg_dataset from name_matching')
    subset_bgg_df.dropna(inplace=True)
    subset_bga_df.dropna(inplace=True)

    # strip of '.0' at the end of each year by converting to int: 2018.0 -> 2018
    subset_bga_df["year_published_bga"] = subset_bga_df["year_published_bga"].astype(int)

    # create dictionary to group all bgg games by their year of publication
    # during the name matching process we will only compare the names of games with the same publication year
    bgg_dic_grouped_by_year = {}
    bga_dic_grouped_by_year = {}

    for year in years:
        bgg_dic_grouped_by_year[year] = subset_bgg_df[subset_bgg_df['year_published_bgg'] == year].to_dict('records')
        bga_dic_grouped_by_year[year] = subset_bga_df[subset_bga_df['year_published_bga'] == year].to_dict('records')

    for year in years:
        for bga_game in bga_dic_grouped_by_year[year]:
            input_string = bga_game['name']

            ref_list = []
            for bgg_game in bgg_dic_grouped_by_year[year]:
                ref_list.append(bgg_game['name'])

            match = find_closest_match(input_string, ref_list, JACCARD_THRESHOLD)
            bga_game['match'] = match['name']
            bga_game['jaccard_score'] = match['jaccard_score']

    bga_list_matches = []
    for year in years:
        for bga_game in bga_dic_grouped_by_year[year]:
            bga_list_matches.append(bga_game)

    # turn list of dictionaries back to data frame:
    jaccard_matches_df = pd.DataFrame(bga_list_matches)

    # just for debugging:
    analyse_df = pd.DataFrame(bga_list_matches)
    analyse_df = analyse_df[analyse_df['jaccard_score'] != '']
    analyse_df = analyse_df[['name', 'match', 'jaccard_score']]
    analyse_df = analyse_df.sort_values('jaccard_score', ascending=False)

    # 1) Create DF containing BGA and BGG IDs of games that could be matched exactly by name and year_published
    # 2) Create DF containing BGA and BGG IDs of games that could be matched by string matching (jaccard method)
    # 3) Concatenate both data frames

    # 1) Exact matches
    # Create dataframes containing only the ids of the games that could be matched exactly
    exact_matches_bgg_df = bgg_df[bgg_df['name'].isin(exact_matches)]
    exact_matches_bga_df = bga_df[bga_df['name'].isin(exact_matches)]

    # Keep only name, year_published and id columns
    exact_matches_bgg_df = exact_matches_bgg_df[['bgg_game_id', 'name', 'year_published']]
    exact_matches_bga_df = exact_matches_bga_df[['bga_game_id', 'name', 'year_published']]

    # Create join:
    exact_matches_join_df = pd.merge(left=exact_matches_bgg_df, right=exact_matches_bga_df,
                                     left_on=['name', 'year_published'], right_on=['name', 'year_published'])

    # Keep only ID columns:
    exact_matches_join_df = exact_matches_join_df[['bgg_game_id', 'bga_game_id']]

    # 2) Jaccard matches
    # Cut of rows where the jaccard threshold wasn't reached (-> no match)
    jaccard_matches_df = jaccard_matches_df[jaccard_matches_df['match'] != '']
    jaccard_matches_df = jaccard_matches_df[['bga_game_id', 'name', 'year_published_bga', 'match', 'jaccard_score']]
    jaccard_matches_df.rename(columns={'name': 'bga_name'}, inplace=True)

    # Join both datasets
    jaccard_matches_join_df = pd.merge(left=bgg_df[['bgg_game_id', 'name', 'year_published']], right=jaccard_matches_df,
                                       left_on=['name', 'year_published'], right_on=['match', 'year_published_bga'])
    jaccard_matches_join_df = jaccard_matches_join_df[['bgg_game_id', 'bga_game_id']]

    # 3) Concat both dfs
    matched_game_ids_df = pd.concat([exact_matches_join_df, jaccard_matches_join_df])

    # 4) Store matches to csv:
    export_df_to_csv(matched_game_ids_df, '../Data/Joined/Integration/GameInformation/matched_bga_and_bgg_ids.csv')


def merge_game_information():
    # import data:
    # bgg game information dataset:
    bgg_filename = get_latest_version_of_file(
        '../Data/BoardGameGeeks/Processed/GameInformation/01_BGG_Game_Information_*.csv')
    bgg_df = pd.read_csv(bgg_filename, index_col=0)
    # bga game information dataset:
    bga_filename = get_latest_version_of_file('../Data/BoardGameAtlas/Processed/API/01_BGA_Game_Information_*.json')
    bga_df = import_json_to_dataframe(bga_filename)

    # this leaves us with four groups:
    # 1) Matched Games
    # 2) BGG Games that could not be matched
    # 3) BGA Games that could not be matched

    # 1) matched games:
    ids_matched_games_df = pd.read_csv('../Data/Joined/Integration/GameInformation/matched_bga_and_bgg_ids.csv',
                                       index_col=0)
    bgg_subset_matches = bgg_df[bgg_df['bgg_game_id'].isin(ids_matched_games_df['bgg_game_id'])]
    bga_subset_matches = bga_df[bga_df['bga_game_id'].isin(ids_matched_games_df['bga_game_id'])]
    # 2) BGG games no matched:
    bgg_subset_no_matches = bgg_df[~bgg_df['bgg_game_id'].isin(ids_matched_games_df['bgg_game_id'])]
    # 3) BGA games no matched:
    bga_subset_no_matches = bga_df[~bga_df['bga_game_id'].isin(ids_matched_games_df['bga_game_id'])]

    # 1)
    # For the matched games there are three types of columns:
    #   a) columns that exist in both datasets but we only need to keep one of them:
    #       (e.g. name, year_published, min_players, ...)
    #       In this case we chose to keep the bgg columns! It doesn't really matter which ones you keep though!
    #   b) columns that exist in both datasets but we want to keep both:
    #       (e.g. bga_game_id/bgg_game_id, num_user_ratings, average_user_rating, bga_rank/bgg_rank, ...)
    #   c) columns that exist only in the bgg dataset:
    #       (e.g. num_user_comments, ...)
    #   d) columns that exist only in the bga dataset:
    #       (e.g. reddit_all_time_count, bga_game_url, ...)

    # 1a) drop columns from bga dataset:
    drop_bga_columns = ['name', 'year_published', 'min_players', 'max_players', 'min_playtime', 'max_playtime',
                        'min_age', 'game_description', 'image_url', 'thumbnail_url']
    bga_subset_matches.drop(columns=drop_bga_columns, inplace=True)

    # add 'matched_bgg_id' column:
    bga_subset_matches = pd.merge(left=bga_subset_matches, right=ids_matched_games_df,
                                  left_on='bga_game_id', right_on='bga_game_id')

    # merge both datasets:
    matched_games_df = pd.merge(left=bgg_subset_matches, right=bga_subset_matches,
                                left_on=['bgg_game_id'], right_on=['bgg_game_id'])

    # Handle duplicate ids in matched_games_df:
    # remove duplicates:
    # duplicate bgg_ids:
    matched_games_df.drop_duplicates(subset=['bgg_game_id'], keep='first', inplace=True)
    # duplicate bga_ids:
    matched_games_df.drop_duplicates(subset=['bga_game_id'], keep='first', inplace=True)

    # In a last (union) step we now have to concatenate all three dataframes to one big dataframes:
    games_df = matched_games_df.append([bgg_subset_no_matches, bga_subset_no_matches], ignore_index=True, sort=False)

    # reorder columns:
    cols_to_order = ['name', 'bgg_game_id', 'bga_game_id', 'year_published', 'min_players', 'max_players',
                     'min_playtime', 'max_playtime', 'min_age', 'bgg_average_user_rating', 'bga_average_user_rating',
                     'bgg_num_user_ratings', 'bga_num_user_ratings']
    new_columns = cols_to_order + (games_df.columns.drop(cols_to_order).tolist())
    games_df = games_df[new_columns]

    # create new unique key_column:
    games_df.insert(0, 'game_key', range(100001, 100001 + len(games_df)))

    # create key_csv that contains bga_game_id, bgg_game_id and game_key:
    key_df = games_df[['game_key', 'bga_game_id', 'bgg_game_id']]

    # check if there are any duplicates
    count_duplicates_bgg = len(key_df[~key_df['bgg_game_id'].isnull()]) - len(
        key_df[~key_df['bgg_game_id'].isnull()].drop_duplicates(subset='bgg_game_id'))
    count_duplicates_bga = len(key_df[~key_df['bga_game_id'].isnull()]) - len(
        key_df[~key_df['bga_game_id'].isnull()].drop_duplicates(subset='bga_game_id'))

    if (count_duplicates_bga + count_duplicates_bga) > 0:
        print('Warning. Duplicates found: ')
        print('BGG_game_ids: ' + str(count_duplicates_bgg))
        print('BGA_game_ids: ' + str(count_duplicates_bga))

    # export to csv:
    export_df_to_csv(games_df, '../Data/Joined/Integration/GameInformation/01_GameInformation_All_Games_Integrated.csv')
    export_df_to_csv(key_df, '../Data/Joined/Integration/GameKeys/Keys_All_Games_Integrated.csv')


def merge_reviews():
    # import reviews:
    bgg_reviews_path = '../Data/BoardGameGeeks/Processed/Reviews/bgg_reviews_15m_CLEANED.csv'
    bga_reviews_path = '../Data/BoardGameAtlas/Processed/API/bga_all_reviews_for_games_with_more_than_2_reviews_CLEANED.csv'

    bgg_reviews = pd.read_csv(bgg_reviews_path, index_col=0)
    bga_reviews = pd.read_csv(bga_reviews_path, index_col=0)

    # import keys:
    key_df = pd.read_csv('../Data/Joined/Integration/GameKeys/Keys_All_Games_Integrated.csv', index_col=0)

    # inner join to get key_column:
    bga_reviews = pd.merge(left=bga_reviews, right=key_df,
                           left_on='game_id', right_on='bga_game_id')

    bgg_reviews = pd.merge(left=bgg_reviews, right=key_df,
                           left_on='game_id', right_on='bgg_game_id')

    # concatenate both dfs:
    all_reviews = pd.concat([bga_reviews, bgg_reviews], ignore_index=True, sort=False)

    # export df:
    export_df_to_csv(all_reviews, '../Data/Joined/Integration/Reviews/Reviews_All_Games_Integrated.csv')


def extract_users():
    # import reviews df:
    reviews_path = '../Data/Joined/Integration/Reviews/Reviews_All_Games_Integrated.csv'
    all_reviews = pd.read_csv(reviews_path, index_col=0)

    # Create user dataframe:
    users_df = all_reviews.groupby(['user_name', 'review_origin']).size().reset_index(name='num_ratings')

    # Count individual users in both datasets:
    bga_users = users_df[users_df['review_origin'] == 'bga']
    sum_bga_users = len(bga_users)
    bgg_users = users_df[users_df['review_origin'] == 'bgg']
    sum_bgg_users = len(bgg_users)
    print('User count:')
    print('BoardGameGeeks users: ' + str(sum_bga_users))
    print('BoardGameAtlas users: ' + str(sum_bgg_users))

    # Add average rating column to user df:
    users_df['avg_rating'] = \
    all_reviews.groupby(['user_name', 'review_origin'], as_index=False).agg({'rating': 'mean'})['rating']

    # Rename origin column:
    users_df.rename(columns={'review_origin': 'user_origin'}, inplace=True)

    # Create user_id:
    users_df.insert(0, 'user_key', range(1, 1 + len(users_df)))

    # Export users to csv:
    export_df_to_csv(users_df, '../Data/Joined/Integration/Users/all_users_integrated.csv')


def clean_reviews():
    # import users:
    users_path = '../Data/Joined/Integration/Users/all_users.csv'
    users_df = pd.read_csv(users_path, index_col=0)
    users_df = users_df[['user_key', 'user_name', 'user_origin']]

    # import reviews:
    reviews_path = '../Data/Joined/Integration/Reviews/Reviews_All_Games_Integrated.csv'
    all_reviews = pd.read_csv(reviews_path, index_col=0)

    # Delete user_id column from review_df which currently holds user_ids from bga_dataset
    # Also delete these columns: review_id, review_date, game_id, bga_game_id and bgg_game_id
    delete_columns = ['user_id', 'review_id', 'review_date', 'game_id', 'bga_game_id', 'bgg_game_id']
    all_reviews.drop(columns=delete_columns, inplace=True)

    # Match user_name and user_id
    all_reviews = pd.merge(left=all_reviews, right=users_df,
                           left_on=['review_origin', 'user_name'], right_on=['user_origin', 'user_name'])

    # Drop columns user_name and review_origin to normalize:
    delete_columns = ['user_name', 'review_origin']
    all_reviews.drop(columns=delete_columns, inplace=True)

    # Change column order:
    cols_to_order = ['game_key', 'user_key', 'rating', 'review_text', 'has_review_text']
    new_columns = cols_to_order + (all_reviews.columns.drop(cols_to_order).tolist())
    all_reviews = all_reviews[new_columns]

    # Export df:
    export_df_to_csv(all_reviews, '../Data/Joined/Integration/Reviews/Reviews_All_Games_Integrated_and_Cleaned.csv')


def find_closest_match(inp_string, ref_list, threshold=0.8):
    # return empty string if ref_list is empty
    if not ref_list:
        return {'name': '', 'jaccard_score': ''}

    jaccard_similarities = []
    ngrams_input_str = ngrams(inp_string)

    for ref_string in ref_list:
        temp = jaccard_similarity(ngrams_input_str, ngrams(ref_string))
        jaccard_similarities.append(temp)

    # get index of highest similarity value:
    index = np.argmax(jaccard_similarities)

    # for debugging only:
    dictionary = {'inp_string': inp_string, 'ref_string': ref_list, 'jaccard_score': jaccard_similarities}
    df = pd.DataFrame(dictionary).sort_values('jaccard_score', ascending=False)

    # only return value if it exceeds threshold
    if jaccard_similarities[index] >= threshold:
        return {'name': ref_list[index], 'jaccard_score': jaccard_similarities[index]}
    else:
        return {'name': '', 'jaccard_score': ''}


def ngrams(string, n=3):
    string = re.sub(r'[,-./]|\sBD', r'', string)

    # add prefix and suffix '##': Uno -> ##Uno##
    # 3-grams: [##U,#Un,Uno,no#,o##]

    # Carcassonno:
    # [##C,#Ca,Car,arc,rca,cas,ass,..,no#,o##]

    # intersection [no#,o##] -> 2
    # union [##U,#Un,Uno,no#,o##,##C,#Ca,Car,arc,rca,cas,ass,..] -> 14

    string = '##' + string + '##'

    # remove common words like 'edition','first','second','third:
    remove_words = ['edition', 'first', 'second', 'third', '2nd', 'deluxe', 'game', 'board', 'card', 'anniversary',
                    'classic', 'collector']

    # split words so that words like 'expEDITION' do not get removed:
    string_words = string.split()
    result_words = [word for word in string_words if word.lower() not in remove_words]
    string = ' '.join(result_words)

    ngrams = zip(*[string[i:] for i in range(n)])
    return [''.join(ngram) for ngram in ngrams]


def jaccard_similarity(list1, list2):
    l1 = set(list1)
    l2 = set(list2)
    intersection = len(l1.intersection(l2))
    union = len(l1.union(l2))
    return float(intersection / union)
