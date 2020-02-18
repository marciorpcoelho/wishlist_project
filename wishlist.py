import urllib.request
import time
from bs4 import BeautifulSoup
import wishlist_info as info


def main():

    # eshop-prices:
    base_url = 'https://eshop-prices.com/'
    for game in info.wish_list:
        print('\nGame: {}'.format(game))
        print('Searching for the game...')

        game_url_name = ''
        game_search_name = game.replace(' ', '+')
        soup = html_soup_retriever(base_url + 'games?q=' + game_search_name)  # First I need to find the corresponding game and respective page

        game_title = title_retrieval(soup)
        print('Game found: {}'.format(game_title))

        print('Searching for prices...')
        for a in soup.find_all('a', href=True):
            if not a['href'].startswith('https:'):
                game_url_name = a['href']
                break  # Makes sure to only match the first result of the search, otherwise it matches the last

        if game_url_name:
            soup = html_soup_retriever(base_url + game_url_name + '?currency=EUR')
            # print(soup.prettify())

            all_prices = prices_retrieval(soup)
            all_countries = countries_retrieval(soup)
            price_and_country_dict = price_and_country_dict_creation(all_prices, all_countries)

            info_parser(price_and_country_dict, info.reference_country, info.top_results_count)
        else:
            print('No link found')

        time.sleep(1)


def html_soup_retriever(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'})
    html = urllib.request.urlopen(req)
    soup = BeautifulSoup(html, 'html.parser')

    return soup


def title_retrieval(soup):
    title = soup.find('h5', {'class': 'games-list-item-title'}).text.strip()

    return title


def prices_retrieval(soup):
    all_prices, all_promotion_dates = [], []

    for td in soup.find_all('td', {'class': 'price-value'}):
        try:
            # Get results which have discount (discounted price and original price)
            values = td.find('div', {'class': 'discounted'}).text
        except (TypeError, AttributeError) as exception:
            # Get results which have no discount (only single price)
            values = td.text

        all_prices.append(values.strip().split(' '))  # For the lack of a better approach for now, ill append all values into a list. They come in pairs, so they should be easy to separate;

    for td in soup.find_all('td', {'class': 'price-meta'}):
        all_promotion_dates.append(td.text.strip())

    for index, promotion_date_end in enumerate(all_promotion_dates):
        all_prices[index].append(promotion_date_end)

    return all_prices


def countries_retrieval(soup):
    all_countries = []
    for td in soup.find_all('td', {'class': ''}):
        td_text = td.text.strip()
        if td_text:
            all_countries.append(td_text)

    return all_countries


def price_and_country_dict_creation(prices, countries):
    data_dict = {country: price for (country, price) in zip(countries[0:len(prices)], prices)}

    return data_dict


def info_parser(price_and_country_dict, reference_country, top_results_shown):
    lowest_price_country = list(price_and_country_dict.keys())[0:top_results_shown]
    # What if a promotion is not lower than a regional price?

    print('Lowest Prices are:')
    for country in lowest_price_country:
        lowest_price = price_and_country_dict[country]
        try:
            # Case when game has promotions going on
            print('Promotion - {} (original price of {}) from {} {} .'.format(lowest_price[1], lowest_price[0], country, lowest_price[2]))
        except IndexError:
            # Case when the game has no promotion going on
            print('{} from {}.'.format(lowest_price[0], country))

    reference_country_analysis(price_and_country_dict, reference_country)


def reference_country_analysis(price_and_country_dict, reference_country):
    reference_price = price_and_country_dict[reference_country]

    try:
        # Case when game has promotions going on
        print('Promotion - Reference price is {} (original price of {}) from {} {}.'.format(reference_price[1], reference_price[0], reference_country, reference_price[2]))
    except IndexError:
        # Case when the game has no promotion going on
        print('Reference price is {} from {}.'.format(reference_price[0], reference_country))


if __name__ == '__main__':
    main()



