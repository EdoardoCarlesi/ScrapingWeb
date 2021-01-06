import numpy as np
import pandas as pd
from urllib.request import Request, urlopen
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time
import numpy
import pandas as pd


def scrape_titles_and_prices(source=None, page_num=None, remote=True): 
    """ Given a page source (ABUgames format!) we extract the card names and all the possible prices """

    # Basic paths and urls
    base_path = 'output/abugames.'
    tmp_out = base_path + str(page_num) + '.html'

    # If reading a remote online page
    if remote:

        # Pass the source file extraced with Selenium 
        soup = BeautifulSoup(source, 'lxml')

        # We do some cleaning as well as a local html copy
        html = soup.prettify()  

        print(f'Exporting to {tmp_out}')

        # Dump the clean version to a temporary output
        with open(tmp_out,"w") as out:
            for i in range(0, len(html)):
                try:
                    out.write(html[i])
                except Exception:
                    pass

    # Read the output from a local source
    else:
        print(f'Extracting from local file: {tmp_out}')

        # Now read the cleaned up version of the file
        soup = BeautifulSoup(open(tmp_out, 'r'), 'lxml')

        # Once we have the page let's find all the card names
        scrape_title = [i.text.replace('\n', '').replace('  ','') for i in soup.find_all("div", {"class":"col-md-3 display-title"})]
        scrape_price = [i.text.replace('\n', '').replace(' ', '').replace('$', '').replace('0.00', '').replace('/','').replace('\\xa0', '')
                .replace('NM', '').replace('Trade', '').replace('HP', '').replace('PLD', '').replace('(','').replace(')', '')
                for i in soup.find_all("span", {"class":"ng-star-inserted"})]

        clean_prices = []
        print(scrape_price)

        for price in scrape_price:
            
            if price == '':
                pass
            else:
                price = float(price)
                clean_prices.append(price)

        print(clean_prices)

        n_titles = len(scrape_title)

        all_prices = np.array(clean_prices)
        all_prices = np.reshape(all_prices, (n_titles, 9))
        df = pd.DataFrame()
        columns = ['CardName', 'PriceNM', 'TradeNM', 'NumNM', 'PricePLD', 'TradePLD', 'NumPLD', 'PriceHP', 'TradeHP', 'NumHP']
        df.columns_ = columns

        df['CardName'] = scrape_title

        for i, col in enumerate(columns[1:]):
            df[col] = all_prices[:, i]

        #print(df.head())
        return df


def get_page_source(url=None, show_browser=False, time_sleep=10, driver=None):
    """ Given a url extract the content and return it """

    # If we don't get the driver from an external source then create a new one
    if driver == None:

        # Open a firefox driver
        if show_browser:
            driver = webdriver.Firefox()

        # Make it run "behind the scenes"
        else:
            options = Options()
            options.add_argument("--headless")
            driver = webdriver.Firefox(options=options)

        driver.get(url)

    # Wait for the page to load correctly
    print('Waiting for the page to load correctly...')
    time.sleep(time_sleep)

    # Once the page has been 
    source = driver.page_source
    
    return source, driver


def extract_cardmarket():
    """ TODO: extract data from cardmarket """
    url = 'https://www.cardmarket.com/en/Magic/Data/Weekly-Top-Cards'
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()
    webs = pd.read_html(webpage)
    print(type(webs[0]))
    print(webs[0].to_csv('output/cardmarket.csv'))
    print(webs)


if __name__ == '__main__':
    """ Main wrapper """
    
    show_browser = False
    remote = True
    url = 'https://abugames.com/buylist?fbclid=IwAR3gw3BG40HBl6LLSIksEhyyqYXW6q511u6LQ9Pt2J63yWBJaOHMyjfe-k4'

    if remote:
        source, driver = get_page_source(url=url, show_browser=show_browser)
    else:
        source = None

    n_pages = 3
    for i in range(1, n_pages+1):

        out_file = 'output/abugames_data_pag.' + str(i) + '.csv'
        data = scrape_titles_and_prices(source=source, page_num=i, remote=remote)
        xpath_str = '//button[contains(text(), "' + str(i) + '")]'
        #xpath_str = '//button[contains(text(), "NEXT")]'

        # Click on the page only if we did not 
        if remote:
            print(f'Page {i} saved to file {out_file}, going to page number: {i}')
            driver.find_element_by_xpath(xpath_str).click() 

            # Wait for some time after clicking on the link so that the page can load correctly
            time.sleep(10)

            # Get the new page source
            source = driver.page_source
            #source, driver = get_page_source(url=url, show_browser=show_browser, driver=driver)
        else:

            data.to_csv(out_file)
       


# WARNING TODO 
'''
    THERE MIGHT BE SOME MINT CARDS. VERY VERY RARE. but this screws up the way things are organized
'''

#print(source)
#/html/body/abu-root/div/abu-public/sd-buylist/section/div/div/div/div[2]/div[2]/div/single-checklist-card-buylist/div/div[3]/div[1]
'''
page = requests.get(url)
print(page.content)
soup = BeautifulSoup(page.content, 'html.parser')
print(soup.prettify())
'''

