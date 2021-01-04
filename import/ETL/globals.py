#####################
# Global variables: #
#####################

# Booleans for main pipeline to decide which functions to call:
RUN_PIPELINE_SPIDER = False
RUN_BGA_GAME_INFO_API_PIPELINE = False
RUN_BGA_REVIEWS_API_PIPELINE = False
RUN_BGG_CLEANING_PIPELINE = False
RUN_INTEGRATION_PIPELINE = True



######################
# Crawler variables: #
######################

# Spiders:
RUN_BOARD_GAME_SPIDER = True
RUN_REVIEW_URL_CRAWLER = False
RUN_RATING_SPIDER = False
RUN_COMMENT_SPIDER = False

# related to Board_Game_Spider
NUM_GAMES_TO_SCRAPE = 120000
STARTING_POINT = 0
