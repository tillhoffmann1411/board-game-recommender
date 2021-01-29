import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

############################################################
######################## CATEGORIES ########################

# creating data frame from csv
df_games_cat = pd.read_csv("E:/github/board-game-recommender/import/Data/Joined/Results/Category_Game_Relation.csv")

# only keeping needed columns
df_games_cat = df_games_cat[["game_key", "category_key"]]

# dropping duplicates
df_games_cat = df_games_cat.drop_duplicates()

# converting category keys to strings
df_games_cat["category_key"]= df_games_cat["category_key"].map(str)

# grouping by game key and aggregating the category keys
df_games_cat2 = df_games_cat.groupby("game_key").agg({"category_key" : ",".join}).reset_index().reindex(columns=df_games_cat.columns)

# separating keys from each other by comma
df_games_cat2["category_key"] = df_games_cat2["category_key"].str.split(",")

# creating boolean matrix for categories
df_games_cat_bool = pd.get_dummies(df_games_cat2["category_key"]
                                  .apply(pd.Series).stack()).groupby(level=0).sum()

# merging boolean matrix with game keys
df_games_cat_bool = df_games_cat2.merge(df_games_cat_bool, how="outer", left_index=True, right_index=True)

# dropping category keys
df_games_cat_bool = df_games_cat_bool.drop(["category_key"], axis=1)

############################################################
######################## MECHANICS #########################

# creating data frame from csv
df_games_mech = pd.read_csv("E:/github/board-game-recommender/import/Data/Joined/Results/Mechanic_Game_Relation.csv")

# only keeping needed columns
df_games_mech = df_games_mech[["game_key", "mechanic_key"]]

# dropping duplicates
df_games_mech = df_games_mech.drop_duplicates()

# converting mechanic keys to strings
df_games_mech["mechanic_key"]= df_games_mech["mechanic_key"].map(str)

# grouping by game key and aggregating the mechanic keys
df_games_mech2 = df_games_mech.groupby("game_key").agg({"mechanic_key" : ",".join}).reset_index().reindex(columns=df_games_mech.columns)

# separating keys from each other by comma
df_games_mech2["mechanic_key"] = df_games_mech2["mechanic_key"].str.split(",")

# creating boolean matrix for mechanics
df_games_mech_bool = pd.get_dummies(df_games_mech2["mechanic_key"]
                                  .apply(pd.Series).stack()).groupby(level=0).sum()

# merging boolean matrix with game keys
df_games_mech_bool = df_games_mech2.merge(df_games_mech_bool, how="outer", left_index=True, right_index=True)

# dropping category keys
df_games_mech_bool = df_games_mech_bool.drop(["mechanic_key"], axis=1)

############################################################
####################### BOARDGAMES #########################

# creating boardgames data frame
df_games = pd.read_csv("E:/github/board-game-recommender/import/Data/Joined/Results/BoardGames.csv")

df_games_num_ratings = df_games[["game_key", "bgg_num_user_ratings", "bga_num_user_ratings"]]

df_games = df_games[["game_key", "name", "bgg_num_user_ratings", "bga_num_user_ratings"]]

df_games = df_games.drop_duplicates()

df_games = df_games.set_index("game_key")

indices = pd.Series(df_games.index, index=df_games['name']).drop_duplicates()

############################################################
#################### MERGING & REDUCING ####################

# merging data frames of boolean categories and mechanics
df_merged = pd.merge(df_games_num_ratings, df_games_cat_bool, on="game_key")
df_merged = pd.merge(df_merged, df_games_mech_bool, on="game_key")

df_merged = df_merged.dropna(axis=0)

df_merged = df_merged[df_merged.bga_num_user_ratings > 5]

df_merged = df_merged.drop(['bgg_num_user_ratings', 'bga_num_user_ratings'], axis=1)

# setting index as game key for clean computing of cosine similarity
df_merged = df_merged.set_index("game_key")

############################################################
########################## COSINE ##########################

# computing the cosine similarity
df_cos = cosine_similarity(df_merged)

# reset index of merge data frame and extracting game keys
df_merged = df_merged.reset_index()
df_game_keys = pd.DataFrame(df_merged["game_key"])

# merging cosine matrix with game keys
df_cos_final = df_game_keys.merge(pd.DataFrame(df_cos), how="outer", left_index=True, right_index=True )

# creating list of game keys
list_cos_final = df_cos_final["game_key"].tolist()

# setting game keys as index
df_cos_final = df_cos_final.set_index("game_key")

# setting game keys as column names
df_cos_final.columns = list_cos_final

df_cos_final = df_cos_final.round(5)

#df_games.to_csv("E:/data/df_games.csv")
#df_cos_final.to_csv("E:/data/df_cos_final.csv")
#indices.to_csv("E:/data/indices.csv")

############################################################
###################### RECOMMENDATION ######################

# Function that takes in board game title as input and outputs most similar boardgames
def get_recommendations(title, cosine_sim = df_cos_final):

    # Get the index of the board game that matches the title
    idx = indices[title]

    # use if index as input
    #idx = title

    # Get the pairwise similarity scores of all games with that game
    sim_scores = list(enumerate(cosine_sim[idx]))

    # Sort the games based on the similarity scores
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Get the scores of the 10 most similar games
    sim_scores = sim_scores[1:11]

    # Get the game indices
    game_indices = [i[0] for i in sim_scores]

    # Return the top 10 most similar games
    return df_games['name'].iloc[game_indices]

# get recommendations for game title
#rec = get_recommendations("Codenames")

def get_recommendations_loop(game_list):
    final_list = []
    for i in game_list:
        final_list.append(get_recommendations(i))
    return final_list

rec = get_recommendations_loop(["Catan", "Codenames"])

breakpoint()