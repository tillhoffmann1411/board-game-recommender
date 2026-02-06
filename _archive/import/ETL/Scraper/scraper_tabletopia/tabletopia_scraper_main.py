from selenium import webdriver
import time
import csv


def get_game_links(save_list=True):
    """
    First part: get and save game links
        1. create selenium webdriver
        2. loop over game overview pages and add a link for each game to a list
        3. save all links as csv
    """

    # create webdriver
    driver = webdriver.Firefox()
    driver.get("https://tabletopia.com/games?")
    time.sleep(2)

    # initialize variables
    link_list = []

    # loop over pages to get links
    for i in range(1, 2, 1):
        # find links to games
        elems = driver.find_elements_by_css_selector('div.item__buttons > a')
        links = [elem.get_attribute('href') for elem in elems]
        # print(links)
        time.sleep(2)

        # extend links to list
        link_list.extend(links)

        # go to next page
        elem = driver.find_element_by_css_selector('#pagination-area > nav > ul > li.pagination__item._next')
        elem.click()
        time.sleep(2)

        print(driver.current_url)

    print("len link_list", len(link_list))
    driver.close()

    # removing irritating links
    link_list.remove('https://tabletopia.com/games/identifica-o-dos-neur-nios')

    # save info as csv
    print(link_list)
    if save_list:
        with open('import/Data/Tabletopia/Raw/tabletopia_links.csv', 'w', newline='') as link_csv:
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
        print("counter:", counter, " - ", link)

        # empty dict each iteration
        info_saver = {
            "game_name_tabletopia": "",
            "game_url_tabletopia": "",
            "player_min_age_tabletopia": "",
            "number_players_tabletopia": "",
            "playing_time_tabletopia": "",
            "rating_tabletopia": "",
            "designer_tabletopia": "",
            "illustrator_tabletopia": "",
            "publisher_tabletopia": "",
            "author_tabletopia": "",
            "genre_tabletopia": "",
            "description_tabletopia": "",
            "bgg_link_tabletopia": ""
        }

        # create webdriver
        driver = webdriver.Firefox()
        driver.get(str(link))
        time.sleep(2)

        # get name
        elem = driver.find_element_by_css_selector('div.detail__title-container > h1').text.strip()
        info_saver['game_name_tabletopia'] = elem

        # get url
        elem = driver.current_url
        info_saver['game_url_tabletopia'] = elem

        # get age
        elem = driver.find_element_by_class_name('game-info__specs').find_element_by_css_selector(
            'div:nth-child(1) > div.specs__text').text.strip()
        info_saver['player_min_age_tabletopia'] = elem

        # get number players
        elem = driver.find_element_by_class_name('game-info__specs').find_element_by_css_selector(
            'div:nth-child(2) > div.specs__text').text.strip()
        info_saver['number_players_tabletopia'] = elem

        # get time
        elem = driver.find_element_by_class_name('game-info__specs').find_element_by_css_selector(
            'div:nth-child(3) > div.specs__text').text.strip()
        info_saver['playing_time_tabletopia'] = elem

        # get rating
        try:
            elem = driver.find_element_by_class_name('game-info__specs').find_element_by_css_selector(
                'div:nth-child(4) > div.specs__text').text.strip()
            info_saver['rating_tabletopia'] = elem
        except:
            info_saver['rating_tabletopia'] = ""

        # get designer
        try:
            elems = driver.find_element_by_class_name('sidebar-section').find_elements_by_css_selector(
                '.sidebar-section__text-block')
            contents = [elem.text.replace('Designer\n', 'Designer: ').replace('Illustrator\n', 'Illustrator: ').replace(
                'Publisher\n', 'Publisher: ').replace('Author\n', 'Author: ').replace('\n', ', ') for elem in elems]
            # order results
            for content in contents:
                if "Designer" in content:
                    info_saver['designer_tabletopia'] = content
                elif "Illustrator" in content:
                    info_saver['illustrator_tabletopia'] = content
                elif "Publisher" in content:
                    info_saver['publisher_tabletopia'] = content
                elif "Author" in content:
                    info_saver['author_tabletopia'] = content
        except:
            info_saver['designer_tabletopia'] = ''
            info_saver['illustrator_tabletopia'] = ''
            info_saver['publisher_tabletopia'] = ''
            info_saver['author_tabletopia'] = ''

        # get genre
        elems = driver.find_elements_by_class_name('game-info__genre')
        content = [elem.text.strip() for elem in elems]
        content = ', '.join(content)
        info_saver['genre_tabletopia'] = content

        # get description
        try:
            elem = driver.find_element_by_id('see-all-description')
            elem.click()
            elem = driver.find_element_by_id('full-description').text
        except:
            elem = driver.find_element_by_class_name('content-list').text
        info_saver['description_tabletopia'] = elem

        # get bgg link
        try:
            elem = driver.find_element_by_class_name('bgg-link').get_attribute('href')
            info_saver['bgg_link_tabletopia'] = elem
        except:
            info_saver['bgg_link_tabletopia'] = ''

        # close driver
        driver.close()

        # add dict to dict_list
        dict_list.append(info_saver)
        # print(dict_list)

        # save all x iterations
        if counter % 25 == 0 or counter == len(links):
            # save info as csv
            keys = dict_list[0].keys()
            if save_csv:
                with open('import/Data/Tabletopia/Raw/tabletopia_all_data_raw.csv', 'w', newline='') as output_file:
                    dict_writer = csv.DictWriter(output_file, keys)
                    dict_writer.writeheader()
                    dict_writer.writerows(dict_list)
        print("done!")


def run_tabletopia_scraper():
    # get all links to game information
    link_list = get_game_links(save_list=False)
    # get game information from each link
    get_game_information(links=link_list, save_csv=False)
