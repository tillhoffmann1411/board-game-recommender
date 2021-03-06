import pandas as pd
import numpy as np
import re

from ETL.globals import MIN_REVIEWS_PER_GAME, MIN_REVIEWS_PER_USER
from ETL.helper import import_json_to_dataframe, get_latest_version_of_file, export_df_to_csv, \
    import_pickle_to_dataframe, export_df_to_pickle
from tabulate import tabulate

# Threshold for matching game names. For jaccard scores lower than that threshold games are no longer matched.
JACCARD_THRESHOLD_GAME_NAME = 0.2

# Counting the number of comparisons when applying our similarity function to game names.
COMPARISONS = 0


def integrate_boardgame_table():
    # match bga and bgg boardgames by applying the set-based similarity function jaccard on the boardgame names.
    match_game_names()

    # merge the bga and bgg game information datasets by using the game matches identified in the previous step
    merge_game_information()


def integrate_user_and_review_tables():
    # merges the reviews of both the bga and bgg dataset
    merge_reviews()

    # create a user table by extracting information from the merged reviews on users from bga and bgg dataset
    extract_users()

    # adds previously created user keys to review table, as well as deletes a few unnecessary or redundant columns
    clean_reviews()


def match_game_names():
    """
    This function matches bga and bgg boardgames based on their game names and the year in which they were published.
    This is how it works:
    - We calculate n-grams with n=3 for each boardgamename.
    - By removing stopwords that appear in many games that don't add much meaning to the game title we can
    reduce the number of false-positives and false-negatives.
    Examples: the stopwords 'board' and 'game' are removed:
        bga_name = '7 Wonders'
        bgg_name = '7 Wonders - The Board Game'
        -> this would result in a rather low jaccard score without removing the stopwords.

        bga_name = 'Settlers - The Board Game'
        bgg_name = '7 Wonder - The Board Game'
        -> this would result in a rather high jaccard score considering that both do not refer to the same game.
    - We then compare the similarity of a bga candidate and a bgg candidate by calculating the jaccard similarity.
    - The candidate with the highest jaccard score is chosen. Only if the jaccard score of that candidate exceeds our
    threshold the games are matched.

    Scalability Challenge:
    - However, there is one issue with that strategy: Computing the jaccard similarity requires comparisons of
    ca. 8,000 bga games and ca. 19,000 bgg games [ O(n) = n^2 ]. Comparing all bga_games and all bgg_games
    would lead to an extremely long run time, which we want to avoid.
    -> 8,000 x 19,000 = 152,000,000 comparisons.

    Therefore we adjusted our approach:
    1) First, we find games that can be matched exactly. By this we mean games that have exactly the same name in both
     datasets. Since there are some games with duplicate game names that do not refer to the same game, we also include
     the year of publication. Therefore only games with exactly the same name and exactly the same year of publication
     are matched in this step. We can then subtract these games from the their datasets to decrease
    the sizes of games that have to be compared to: ca. 3,000 bga games and ca. 15,000 bgg games.
    -> 3,000 x 15,000 = 45,000,000 (complexity reduced by ~70%)
    2) This is still quite a lot of comparisons. However, we made another observation. We also tried matching games
    by only their game_name (not also taking the year_published into consideration). In the set of games that could
    be matched exactly, in almost all cases the publish years are the same, which makes sense obviously.
    3) Therefore we can further reduce complexity by grouping by publish years and comparing only games that have
    the same publish year. To make sure we don't lose games because the publish years deviate by one year, we also
    compare to games published in the years one year before and after.
    This further reduces the number of comparisons to: ~ 1,000,000
    Hence, by applying the similarity function only to the most promising pairs we reduced the number of required
    comparisons by 98%.
    """

    # Import bgg and bga data:
    bgg_filename = get_latest_version_of_file(
        '../Data/BoardGameGeeks/Processed/GameInformation/01_BGG_Game_Information_*.csv')
    bgg_df = pd.read_csv(bgg_filename, index_col=0)
    bgg_names = bgg_df['name'].tolist()

    bga_filename = get_latest_version_of_file('../Data/BoardGameAtlas/Processed/API/01_BGA_Game_Information_*.json')
    bga_df = import_json_to_dataframe(bga_filename)
    bga_names = bga_df['name'].tolist()

    # Create lists with bga and bgg ids:
    bgg_ids = bgg_df['bgg_game_id'].tolist()
    bga_ids = bga_df['bga_game_id'].tolist()

    # Check duplicate names:
    bgg_duplicate_names = set([x for x in bgg_names if bgg_names.count(x) > 1])
    bga_duplicate_names = set([x for x in bga_names if bga_names.count(x) > 1])

    ## find exact matches (game_name, year_published):
    exact_matches_join_df = pd.merge(left=bgg_df, right=bga_df,
                                     left_on=['name', 'year_published'], right_on=['name', 'year_published'])

    # create list of ids of exactly matched games:
    exact_matches_bgg_ids = exact_matches_join_df['bgg_game_id'].tolist()
    exact_matches_bga_ids = exact_matches_join_df['bga_game_id'].tolist()

    # subtract exact matches from datasets to reduce their size:
    subset_bgg_df = bgg_df[~bgg_df['bgg_game_id'].isin(exact_matches_bgg_ids)]
    subset_bga_df = bga_df[~bga_df['bga_game_id'].isin(exact_matches_bga_ids)]
    subset_bgg_df.rename(columns={'year_published': 'year_published_bgg'}, inplace=True)
    subset_bga_df.rename(columns={'year_published': 'year_published_bga'}, inplace=True)


    ## In the next part we now want to apply name matching. Our first task is to find candidates so that we don't
    ## have to compare all games from one dataset with all games from the other dataset. We do so by grouping by
    ## their year of publication.
    ## First, we need some preprocessing steps so that we can actually set up our candidates:

    # Extract years from bga dataset:
    # A lot of type casting due to unexpected errors with float and set
    all_years = subset_bga_df['year_published_bga'].dropna().tolist()
    all_years = list(map(int, all_years))
    years = list(set(all_years))
    years.sort(reverse=True)

    # Do not apply name matching to games where to publish_year is missing:
    print('Dropped ' + str(subset_bgg_df['year_published_bgg'].isna().sum()) +
          ' rows from bga_dataset from name_matching')
    print('Dropped ' + str(subset_bga_df['year_published_bga'].isna().sum()) +
          ' rows from bgg_dataset from name_matching')
    subset_bgg_df.dropna(inplace=True)
    subset_bga_df.dropna(inplace=True)

    # strip of '.0' at the end of each year by converting to int: 2018.0 -> 2018
    subset_bga_df["year_published_bga"] = subset_bga_df["year_published_bga"].astype(int)

    # create a dictionary to group all bgg games by their year of publication
    # during the name matching process we will only compare the names of games with the same publication year
    bgg_dic_grouped_by_year = {}
    bga_dic_grouped_by_year = {}

    # fill the previously created dictionaries that include all the games that were published in a certain year
    for year in years:
        bgg_dic_grouped_by_year[year] = subset_bgg_df[subset_bgg_df['year_published_bgg'] == year].to_dict('records')
        bga_dic_grouped_by_year[year] = subset_bga_df[subset_bga_df['year_published_bga'] == year].to_dict('records')


    ## Now we get to the interesting part:
    ## We iterate over all bga_games which we found no exact bgg_matches for. We then create a list with potential
    ## candidates including all bgg_games that were published in the same year or one year before or after.
    ## For these candidates we then apply name_matching using the jaccard similarity.
    for year in years:
        for bga_game in bga_dic_grouped_by_year[year]:
            input_string = bga_game['name']

            candidate_list = []
            # create candidate_list with all bgg games that were published in the same year as the bga_game:
            for bgg_game in bgg_dic_grouped_by_year[year]:
                candidate_list.append(bgg_game['name'])

            # also check bgg games that were published in the previous year and one year later:
            if year+1 in bgg_dic_grouped_by_year:
                for bgg_game in bgg_dic_grouped_by_year[year+1]:
                    candidate_list.append(bgg_game['name'])
            if year-1 in bgg_dic_grouped_by_year:
                for bgg_game in bgg_dic_grouped_by_year[year-1]:
                    candidate_list.append(bgg_game['name'])

            # Try to match the input_string (target BGA Game name) one of the games in the candidate_list (bgg games).
            # The match with the highest jaccard similarity is returned. If there is no match, or the Jaccard threshold
            # can not be exceeded then an empty string is returned.
            match = find_match(input_string, candidate_list, JACCARD_THRESHOLD_GAME_NAME)
            bga_game['match'] = match['name']
            bga_game['jaccard_score'] = match['jaccard_score']

    global COMPARISONS
    print('Number of comparisons: '+str(COMPARISONS))

    bga_list_matches = []
    for year in years:
        for bga_game in bga_dic_grouped_by_year[year]:
            bga_list_matches.append(bga_game)

    # turn list of dictionaries back to data frame:
    jaccard_matches_df = pd.DataFrame(bga_list_matches)

    # just for debugging and inspecting results:
    analyse_df = pd.DataFrame(bga_list_matches)
    analyse_df = analyse_df[analyse_df['jaccard_score'] != '']
    analyse_df = analyse_df[['name', 'match', 'jaccard_score']]
    analyse_df = analyse_df.sort_values('jaccard_score', ascending=False)


    ## We have now succesfully found a large number of games that could be matched. All that's left to do is
    #  creating a dataframe that contains the matched BGA and BGG IDs. We do so in three steps:
    # 1) Prepare DF containing BGA and BGG IDs of games that could be matched exactly by name and year_published
    # 2) Prepare DF containing BGA and BGG IDs of games that could be matched by string matching (jaccard method)
    # 3) Concatenate both data frames

    # 1) Exact matches
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
    '''
    Function merges the boardgames of the previously matched games.

    For the matched games there are four types of columns:
        a) columns that exist in both datasets but we only need to keep one of them (can include conflicting values):
            (e.g. name, year_published, min_players, ...)
            In this case we chose to keep the bgg columns! ["trust-your-friends" avoidance strategy as in case of
            contradicting values we keep values based on which data source they come from]
        b) columns that exist in both datasets but we want to keep both:
            (e.g. bga_game_id/bgg_game_id, num_user_ratings, average_user_rating, bga_rank/bgg_rank, ...)
        c) columns that exist only in the bgg dataset:
            (e.g. num_user_comments, bgg_average_weight, ...)
        d) columns that exist only in the bga dataset:
            (e.g. reddit_all_time_count, bga_game_url, ...)
    '''
    # import data:
    # bgg game information dataset:
    bgg_filename = get_latest_version_of_file(
        '../Data/BoardGameGeeks/Processed/GameInformation/01_BGG_Game_Information_*.csv')
    bgg_df = pd.read_csv(bgg_filename, index_col=0)
    # bga game information dataset:
    bga_filename = get_latest_version_of_file('../Data/BoardGameAtlas/Processed/API/01_BGA_Game_Information_*.json')
    bga_df = import_json_to_dataframe(bga_filename)

    # 1) this leaves us with three groups:
    # a) Matched Games
    # b) BGG Games that could not be matched
    # c) BGA Games that could not be matched

    # 1a) matched games:
    ids_matched_games_df = pd.read_csv('../Data/Joined/Integration/GameInformation/matched_bga_and_bgg_ids.csv',
                                       index_col=0)
    bgg_subset_matches = bgg_df[bgg_df['bgg_game_id'].isin(ids_matched_games_df['bgg_game_id'])]
    bga_subset_matches = bga_df[bga_df['bga_game_id'].isin(ids_matched_games_df['bga_game_id'])]
    # 1b) BGG games no matched:
    bgg_subset_no_matches = bgg_df[~bgg_df['bgg_game_id'].isin(ids_matched_games_df['bgg_game_id'])]
    # 1c) BGA games no matched:
    bga_subset_no_matches = bga_df[~bga_df['bga_game_id'].isin(ids_matched_games_df['bga_game_id'])]

    # 2)
    # For the matched games there are three types of columns:
    #   a) columns that exist in both datasets but we only need to keep one of them:
    #       (e.g. name, year_published, min_players, ...)
    #       In this case we chose to keep the bgg columns! It doesn't really matter which ones you keep though!
    #   b) columns that exist in both datasets but we want to keep both:
    #       (e.g. bga_game_id/bgg_game_id, num_user_ratings, average_user_rating, bga_rank/bgg_rank, ...)
    #   c) columns that exist only in the bgg dataset:
    #       (e.g. num_user_comments, bgg_average_weight, ...)
    #   d) columns that exist only in the bga dataset:
    #       (e.g. reddit_all_time_count, bga_game_url, ...)

    # 2a) drop columns from bga dataset:
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

    # check if there are any duplicates in game_df:
    games_df_duplicates = len(games_df)-len(games_df.drop_duplicates())

    if games_df_duplicates > 0:
        print('Warning. ' + str(games_df_duplicates) + ' duplicates found in BoardGameTable: ')
        games_df.drop_duplicates(inplace=True)
        print('Duplicates removed!')

    # check if there are any duplicates in key_df:
    count_duplicates_bgg = len(key_df[~key_df['bgg_game_id'].isnull()]) - len(
        key_df[~key_df['bgg_game_id'].isnull()].drop_duplicates(subset='bgg_game_id'))
    count_duplicates_bga = len(key_df[~key_df['bga_game_id'].isnull()]) - len(
        key_df[~key_df['bga_game_id'].isnull()].drop_duplicates(subset='bga_game_id'))

    if (count_duplicates_bga + count_duplicates_bga) > 0:
        print('Warning. Duplicates found: ')
        print('BGG_game_ids: ' + str(count_duplicates_bgg))
        print('BGA_game_ids: ' + str(count_duplicates_bga))
        key_df.drop_duplicates(inplace=True)
        print('Duplicates removed:')

    # Fix badly encoded symbols
    # Insert quotation marks
    games_df['game_description'] = games_df['game_description'].str.replace(r'&quot;', '\'')
    games_df['game_description'] = games_df['game_description'].str.replace(r'&rdquo;', '\'')
    games_df['game_description'] = games_df['game_description'].str.replace(r'&rsquo;', '\'')
    games_df['game_description'] = games_df['game_description'].str.replace(r'&ldquo;', '\'')
    games_df['game_description'] = games_df['game_description'].str.replace(r'&amp;', '&')
    games_df['game_description'] = games_df['game_description'].str.replace(r'&eacute;', 'e')

    # Insert Umlaute
    games_df['game_description'] = games_df['game_description'].str.replace(r'&auml;', 'ä')
    games_df['game_description'] = games_df['game_description'].str.replace(r'&Uuml;', 'ü')
    games_df['game_description'] = games_df['game_description'].str.replace(r'&uuml;', 'ü')
    games_df['game_description'] = games_df['game_description'].str.replace(r'&ouml;', 'ö')
    games_df['game_description'] = games_df['game_description'].str.replace(r'&szlig;', 'ß')

    # Insert dashes & non-breaking space
    games_df['game_description'] = games_df['game_description'].str.replace(r'&ndash;', '-')
    games_df['game_description'] = games_df['game_description'].str.replace(r'&mdash;', '-')
    games_df['game_description'] = games_df['game_description'].str.replace(r'&nbsp;', ' ')
    games_df['game_description'] = games_df['game_description'].str.replace(r'&times;', 'x')
    games_df['game_description'] = games_df['game_description'].str.replace(r'&shy;', '-')

    # Kick html characters
    games_df['game_description'] = games_df['game_description'].str.replace(r'&#...;', '')
    games_df['game_description'] = games_df['game_description'].str.replace(r'&#..;', ' ')
    games_df['game_description'] = games_df['game_description'].str.replace(r'&#.;', '')

    games_df['game_description'] = games_df['game_description'].str.replace(r'.....;', '')
    games_df['game_description'] = games_df['game_description'].str.replace(r'....;', '')
    games_df['game_description'] = games_df['game_description'].str.replace(r'...;', '')
    games_df['game_description'] = games_df['game_description'].str.replace(r'..;', '')
    games_df['game_description'] = games_df['game_description'].str.replace(r'.;', '')

    # Remove double semicolon and double spaces
    games_df['game_description'] = games_df['game_description'].str.replace(r';;', ' ')
    games_df['game_description'] = games_df['game_description'].str.replace(' +', ' ')
    games_df['game_description'] = games_df['game_description'].str.strip()

    # export to csv:
    export_df_to_csv(games_df, '../Data/Joined/Results/BoardGames.csv')
    export_df_to_csv(key_df, '../Data/Joined/Integration/GameKeys/Keys_All_Games_Integrated.csv')


def merge_reviews():
    # import reviews:
    bgg_reviews_path = '../Data/BoardGameGeeks/Processed/Reviews/bgg_reviews_15m_CLEANED.pickle'
    bga_reviews_path = '../Data/BoardGameAtlas/Processed/API/bga_all_reviews_for_games_with_more_than_2_reviews_CLEANED.csv'

    bga_reviews = pd.read_csv(bga_reviews_path, index_col=0)
    bgg_reviews = import_pickle_to_dataframe(bgg_reviews_path)


    # remove index column from bgg_reviews. Including index_col=0 in the read_csv statement did not work for some unknown reason.
    bgg_reviews.drop(bgg_reviews.columns[0], axis=1)

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
    export_df_to_pickle(all_reviews, '../Data/Joined/Integration/Reviews/Reviews_All_Games_Integrated.pickle')


def extract_users():
    # import reviews df:
    reviews_path = '../Data/Joined/Integration/Reviews/Reviews_All_Games_Integrated.pickle'
    all_reviews = import_pickle_to_dataframe(reviews_path)
    # remove index column from all_reviews.
    # Including index_col=0 in the read_csv statement throws an error for some unknown reason.
    all_reviews.drop(all_reviews.columns[0], axis=1)

    # Create user dataframe:
    users_df = all_reviews.groupby(['user_name', 'review_origin']).size().reset_index(name='num_ratings')

    # Count individual users in both datasets:
    bga_users = users_df[users_df['review_origin'] == 'bga']
    sum_bga_users = len(bga_users)
    bgg_users = users_df[users_df['review_origin'] == 'bgg']
    sum_bgg_users = len(bgg_users)
    print('User count:')
    print('BoardGameAtlas users: ' + str(sum_bga_users))
    print('BoardGameGeeks users: ' + str(sum_bgg_users))

    # Add average rating column to user df:
    users_df['avg_rating'] = all_reviews.groupby(['user_name', 'review_origin'], as_index=False).agg({'rating': 'mean'})['rating']

    # Rename origin column:
    users_df.rename(columns={'review_origin': 'user_origin'}, inplace=True)

    # Create user_id:
    users_df.insert(0, 'user_key', range(1, 1 + len(users_df)))

    # Export users to csv:
    export_df_to_csv(users_df, '../Data/Joined/Results/User.csv')


def clean_reviews():
    # import users:
    users_path = '../Data/Joined/Results/User.csv'
    users_df = pd.read_csv(users_path, index_col=0)
    users_df = users_df[['user_key', 'user_name', 'user_origin']]

    # import reviews:
    reviews_path = '../Data/Joined/Integration/Reviews/Reviews_All_Games_Integrated.pickle'
    all_reviews = import_pickle_to_dataframe(reviews_path)

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

    # Drop text columns since we do not use them and they take away a lot of memory:
    del all_reviews['review_text']

    ## Take care of duplicates:
    # check if there are any duplicates
    count_duplicates = len(all_reviews)-len(all_reviews.drop_duplicates(subset=['game_key', 'user_key'], keep='first'))

    if count_duplicates > 0:
        print('Warning. Duplicates ' + str(count_duplicates) + ' found: ')

        # remove duplicates:
        all_reviews.drop_duplicates(subset=['game_key', 'user_key'], keep='first', inplace=True)
        print('Found duplicates removed!')


    ## Keep only reviews of users with a certain amount of ratings and reviews of games with >= ... ratings:
    print('Removing reviews of games with less than ' + str(MIN_REVIEWS_PER_GAME) +
          ' reviews and users with less than '+str(MIN_REVIEWS_PER_USER)+' reviews.')

    reviews_full_dataset = len(all_reviews)
    games_full_dataset = all_reviews['game_key'].nunique()
    users_full_dataset = all_reviews['user_key'].nunique()

    # keep only reviews of games with >= ... reviews:
    num_reviews_per_game = all_reviews.game_key.value_counts()
    all_reviews = all_reviews[all_reviews.game_key.isin(
        num_reviews_per_game.index[num_reviews_per_game.ge(MIN_REVIEWS_PER_GAME)])]

    # keep only reviews of users with >= ... reviews:
    num_reviews_per_user = all_reviews.user_key.value_counts()
    all_reviews = all_reviews[all_reviews.user_key.isin(
        num_reviews_per_user.index[num_reviews_per_user.ge(MIN_REVIEWS_PER_USER)])]

    ## Track changes:
    # Count reviews, games and users in reduced dataset:
    reviews_reduced_dataset = len(all_reviews)
    games_reduced_dataset = all_reviews['game_key'].nunique()
    users_reduced_dataset = all_reviews['user_key'].nunique()

    # Calculate absolute number of dropped values:
    reviews_dropped_abs = reviews_full_dataset - reviews_reduced_dataset
    games_dropped_abs = games_full_dataset - games_reduced_dataset
    users_dropped_abs = users_full_dataset - users_reduced_dataset

    # Calculate relative number of dropped values:
    reviews_dropped_rel = reviews_dropped_abs / reviews_full_dataset
    games_dropped_rel = games_dropped_abs / games_full_dataset
    users_dropped_rel = users_dropped_abs / users_full_dataset

    # Create a nice table to visualize the results:
    table = [['Reviews', reviews_full_dataset, reviews_reduced_dataset, reviews_dropped_abs, reviews_dropped_rel],
            ['Games', games_full_dataset, games_reduced_dataset, games_dropped_abs, games_dropped_rel],
            ['Users', users_full_dataset, users_reduced_dataset, users_dropped_abs, users_dropped_rel]]

    print(tabulate(table, headers=['_', 'Count (full dataset)', 'Count (reduced dataset)', 'Num dropped (absolute)', 'Num dropped (relative)']))

    # Calculate the size of the utility matrix, prior and after reducing the dataset:
    size_utility_matrix_full_dataset = games_full_dataset * users_full_dataset
    size_utility_matrix_reduced_dataset = games_reduced_dataset * users_reduced_dataset

    print('Reviews dropped: ' + str(reviews_dropped_rel*100)+' %')
    print('Utility matrix full dataset: ' + str(games_full_dataset) + ' * ' + str(users_full_dataset))
    print('Utility matrix reduced dataset: ' + str(games_reduced_dataset) + ' * ' + str(users_reduced_dataset))

    print('Size of utility matrix reduced by: ' + str(100*(1-(size_utility_matrix_reduced_dataset/size_utility_matrix_full_dataset))) + ' %')

    # Export df:
    export_df_to_csv(all_reviews, '../Data/Joined/Results/Reviews_Reduced.csv')


def find_match(inp_string, ref_list, threshold=0.8):
    """
    Returns the element in the ref_list that is most similar to the inp_string by calculating the jaccard similarity
    for each element in the ref_list. If the match with the highest score does not exceed a threshold and empty
    match and jaccard_score is returned.
    """
    # return empty string if ref_list is empty
    if not ref_list:
        return {'name': '', 'jaccard_score': ''}

    jaccard_similarities = []

    # creates the ngrams for the inp_string
    ngrams_input_str = ngrams(inp_string)

    # iterates over all elements in the ref_list and calculates the jaccard similarity for each candidate
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
    """
    Returns a list containing the n-grams of the passed string.
    Punctuation marks as well as stopwords are removed. Also a "##" prefix and suffix is added as suggested in
    Chapter 03 - Finding Similar Items in J. Lescovec, A. Rajaraman, J.D. Ullman - Mining of Massive Data Sets (2019).
    http://www.mmds.org/
    """

    # removes punctuation marks:
    string = re.sub(r'[,-./:!?)(\']|\sBD', r'', string)

    # remove common words like 'edition','first','second','third:
    remove_words = ['edition', 'first', 'second', 'third', '2nd', 'deluxe', 'game', 'board', 'card', 'anniversary',
                    'classic', 'collector', 'strategy', '3rd', '4th', '5th', 'third', 'fourth', 'fifth', 'the']

    # split words so that words like 'expEDITION' do not get removed:
    string_words = string.split()
    result_words = [word for word in string_words if word.lower() not in remove_words]
    string = ' '.join(result_words)
    string = string.strip()

    # add prefix and suffix '##': Uno -> ##Uno##
    # 3-grams: [##U,#Un,Uno,no#,o##]
    string = '##' + string + '##'

    # last two lines based on this blog: https://albertauyeung.github.io/2018/06/03/generating-ngrams.html
    ngrams = zip(*[string[i:] for i in range(n)])
    return [''.join(ngram) for ngram in ngrams]


def jaccard_similarity(list1, list2):
    global COMPARISONS
    COMPARISONS = COMPARISONS + 1
    l1 = set(list1)
    l2 = set(list2)
    intersection = len(l1.intersection(l2))
    union = len(l1.union(l2))
    return float(intersection / union)
