#####################
# ETL pipeline variables: #
#####################

# Booleans for main pipeline to decide which functions to call:
RUN_BGA_PIPELINE = True
RUN_BGG_PIPELINE = False
RUN_SCRAPE_ONLINE_GAMES_PIPELINE = False
RUN_INTEGRATE_OFFLINE_GAMES_PIPELINE = False
RUN_INTEGRATE_ONLINE_GAMES_PIPELINE = False
RUN_UPLOAD = True

# Parameters for which users and games to keep in reviews:
# Keep only games with >= ... reviews:
MIN_REVIEWS_PER_GAME = 500

# Keep only users with >= ... reviews:
MIN_REVIEWS_PER_USER = 5


######################
# Crawler variables: #
######################

# Spiders:
RUN_BOARD_GAME_SPIDER = False
RUN_REVIEW_URL_CRAWLER = False
RUN_RATING_SPIDER = False
RUN_COMMENT_SPIDER = False
