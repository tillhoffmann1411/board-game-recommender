#####################
# Global variables: #
#####################

# Booleans for main pipeline to decide which functions to call:
RUN_PIPELINE_BGA_SPIDER = False
RUN_BGA_GAME_INFO_API_PIPELINE = False
RUN_BGA_REVIEWS_API_PIPELINE = False
RUN_BGG_CLEANING_PIPELINE = False
RUN_INTEGRATION_PIPELINE = False
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
