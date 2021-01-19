from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
import time
import csv
import os

path = 'C:\\Users\\Benjamin\\Documents\\GitHub\\board-game-recommender\\import\\Data\\Boardgamearena\\Raw'

try:
    os.mkdir(path)
except OSError:
    print("Creation of the directory %s failed" % path)
else:
    print("Successfully created the directory %s " % path)
filename = 'C:\\Users\\Benjamin\\Documents\\GitHub\\board-game-recommender\\import\\Data\\Boardgamearena\\Raw\\test.txt'
if os.path.exists(filename):
    append_write = 'a'  # append if already exists
else:
    append_write = 'w'  # make a new file if not

highscore = open(filename, append_write)
highscore.write('Fucking finally')
highscore.close()

pathdata = 'C:\\Users\\Benjamin\\Documents\\GitHub\\board-game-recommender\\import\\Data\\Boardgamearena\\Raw'
datafilename = 'C:\\Users\\Benjamin\\Documents\\GitHub\\board-game-recommender\\import\\Data\\Boardgamearena\\Boardgamearena_all_raw'


def unique(link_list):
    unique_link_list = []
    for x in link_list:
        if x not in unique_link_list:
            unique_link_list.append(x)

def get_game_links(save_list=True, elem=None):
    """
    First part: get and save game links
        1. create selenium webdriver
        2. loop over game overview pages and add a link for each game to a list
        3. save all links as csv
    """

    # create webdriver
    #  binary = FirefoxBinary(C:\Program Files\Mozilla Firefox\firefox.exe)
    driver = webdriver.Firefox()
    driver.get("https://de.boardgamearena.com/gamelist?section=all")
    time.sleep(2)

    # initialize variables
    link_list = []
    # loop over pages to get links
    for i in range(1, 2, 1):
        # find links to games
        elems = driver.find_elements_by_class_name('gamelist_item a')
        links = [elem.get_attribute('href') for elem in elems]

        time.sleep(2)

        # extend links to list
        link_list.extend(links)

        # go to next page
        # elem = driver.find_element_by_css_selector('#pagination-area > nav > ul > li.pagination__item._next')
        # elem.click()
        # time.sleep(2)

    #   print(driver.current_url)

    print("len link_list", len(link_list))
    driver.close()

    link_list.remove('https://de.boardgamearena.com/gamepanel?game=tzolkin')
    link_list.remove('https://de.boardgamearena.com/gamepanel?game=k2')
    link_list.remove('https://de.boardgamearena.com/gamepanel?game=koryo')
    unique(link_list)



    # removing irritating links (fucking czech and their stupid acutes and carons)

    # save info as csv
    print(link_list)
    if save_list:

        try:
            os.mkdir(pathdata)
        except OSError:
            print("Creation of the directory %s failed" % path)
        else:
            print("Successfully created the directory %s " % path)

        with open(datafilename, 'w', newline='') as link_csv:
            wr = csv.writer(link_csv, quoting=csv.QUOTE_ALL)
            wr.writerow(link_list)

    return link_list


def get_game_information(links, save_csv=True):
    """
    Second part: get and save game information
        1. use links to get to game information page
        2. create dict to collect information for each game
        3. loop over links and save game information on dict
        4. save game information as csv
    """
    # initialize variables
    dict_list = []
    counter = 0

    # get info for each link on link list
    for link in links:
        # counter info
        counter = counter + 1
        print("Verarbeitet:", counter, " - ", link)

        # empty dict each iteration
        info_saver = {
            "game_name_boardgamearena": "",
            "game_url_boardgamearena": "",
            "number_players_boardgamearena": "",
            "playing_time_boardgamearena": "",
            "game_complexity_boardgamearena": "",
            "game_strategy_boardgamearena": "",
            "game_luck_boardgamearena": "",
            "game_interaction_boardgamearena": "",
            "rounds_played_boardgamearena": "",
            "available_since_boardgamearena": "",
            "version_boardgamearena": "",
            "description_boardgamearena": "",
            "author_name_boardgamearena": "",
            "graphicer_name_boardgamearena": "",
            "publisher_name_boardgamearena": "",
            "basegame_release_year_boardgamearena": "",
            "developer_name_boardgamearena": ""
        }

        # create webdriver
        driver = webdriver.Firefox()
        driver.get(str(link))
        #  time.sleep(1)

        # Expand Webpage
        elem = driver.find_element_by_id('game_readmore')
        elem.click()
        # time.sleep(1)

        # get name
        elem = driver.find_element_by_class_name('gamename').text.strip()
        info_saver['game_name_boardgamearena'] = elem

        # get description
        elem = driver.find_element_by_id('game_description_text').text.strip()
        info_saver['description_boardgamearena'] = elem

        # get url
        elem = driver.current_url
        info_saver['game_url_boardgamearena'] = elem

        # get total rounds played
        elem = driver.find_element_by_id('game_lastresults').text.strip()
        info_saver['rounds_played_boardgamearena'] = elem

        # get number players
        elem = driver.find_element_by_class_name('col-md-5').find_element_by_css_selector(
            'div:nth-child(2) > div.row-value').text.strip()
        info_saver['number_players_boardgamearena'] = elem

        # get time
        elem = driver.find_element_by_class_name('col-md-5').find_element_by_css_selector(
            'div:nth-child(3) > div.row-value').text.strip()
        info_saver['playing_time_boardgamearena'] = elem

        # get complexity
        elem = driver.find_element_by_class_name('col-md-5').find_element_by_css_selector(
            'div:nth-child(4) > div.row-value').text.strip()
        info_saver['game_complexity_boardgamearena'] = elem

        # get strategy rating
        elem = driver.find_element_by_class_name('col-md-5').find_element_by_css_selector(
            'div:nth-child(5) > div.row-value').text.strip()
        info_saver['game_strategy_boardgamearena'] = elem

        # get luck rating
        elem = driver.find_element_by_class_name('col-md-5').find_element_by_css_selector(
            'div:nth-child(6) > div.row-value').text.strip()
        info_saver['game_luck_boardgamearena'] = elem

        # get interaction rating
        elem = driver.find_element_by_class_name('col-md-5').find_element_by_css_selector(
            'div:nth-child(7) > div.row-value').text.strip()
        info_saver['game_interaction_boardgamearena'] = elem

        # get aviable since
        elem = driver.find_element_by_class_name('col-md-5').find_element_by_css_selector(
            'div:nth-child(8) > div.row-value').text.strip()
        info_saver['available_since_boardgamearena'] = elem

        # get version number
        elem = driver.find_element_by_class_name('col-md-5').find_element_by_css_selector(
            'div:nth-child(9) > div.row-value').text.strip()
        info_saver['version_boardgamearena'] = elem

        # get author name
        elem = driver.find_element_by_class_name('col-md-4.game_infos_first_col').find_element_by_css_selector(
            'div:nth-child(1) > div.row-value').text.strip()
        info_saver['author_name_boardgamearena'] = elem

        # get graphicer name
        elem = driver.find_element_by_class_name('col-md-4.game_infos_first_col').find_element_by_css_selector(
            'div:nth-child(2) > div.row-value').text.strip()
        info_saver['graphicer_name_boardgamearena'] = elem

        # get original publisher
        elem = driver.find_element_by_class_name('col-md-4.game_infos_first_col').find_element_by_css_selector(
            'div:nth-child(3) > div.row-value').text.strip()
        info_saver['publisher_name_boardgamearena'] = elem

        # get release year of original board game
        elem = driver.find_element_by_class_name('col-md-4.game_infos_first_col').find_element_by_css_selector(
            'div:nth-child(4) > div.row-value').text.strip()
        info_saver['basegame_release_year_boardgamearena'] = elem

        # get developer name
        elem = driver.find_element_by_class_name('col-md-4.game_infos_first_col').find_element_by_css_selector(
            'div:nth-child(4) > div.row-value').text.strip()
        info_saver['developer_name_boardgamearena'] = elem

        # close driver
        driver.close()

        # add dict to dict_list
        dict_list.append(info_saver)
        print(dict_list)

        # save all x iterations
        if counter % 25 == 0 or counter == len(links):
            # save info as csv
            keys = dict_list[0].keys()
            if save_csv:
                with open(datafilename, 'w',
                          newline='') as output_file:
                    dict_writer = csv.DictWriter(output_file, keys)
                    dict_writer.writeheader()
                    dict_writer.writerows(dict_list)
        print("Fettich!")


if __name__ == "__main__":
    # get all links to game information
    link_list = get_game_links(save_list=True)
    #  get game information from each link
    get_game_information(links=link_list, save_csv=True)
