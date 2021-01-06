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
    #base_path = 'output/abugames_mox.'
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
                .replace('Trade', '').replace('(','').replace(')', '').replace(',', '')
                #.replace('NM', '').replace('HP', '').replace('PLD', '')
                for i in soup.find_all("span", {"class":"ng-star-inserted"})]

        clean_prices = []
        for price in scrape_price:
            if price == '':
                pass
            else:
                clean_prices.append(price)

        # Initialize some variables used to store the elements into arrays
        n_rows = len(scrape_title)
        all_prices = np.zeros((n_rows, 9))
        n_elements = len(clean_prices)

        # Initialize some counters and other variables used in the loop over rows
        counter = 0
        price = clean_prices[counter]

        card_types = ['MINT', 'NM', 'HP', 'PLD']

        if price in card_types:
            pass
        else:
            clean_prices.remove(price)
            n_elements -= 1

        price = clean_prices[counter]

        #print(clean_prices)

        #The table might have some missing elements, so we need to fill everything up keeping in mind that some elements will be missing
        for i_row in range(0, n_rows): 

            # Just ignore mint, it's a very rare occurrence
            if price == 'MINT':
                counter += 4
                price = clean_prices[counter]
                print(price)

            if price == 'NM': 
                counter += 1
                all_prices[i_row, 0] = float(clean_prices[counter])
                counter += 1
                all_prices[i_row, 1] = float(clean_prices[counter])
                counter += 1
                all_prices[i_row, 2] = float(clean_prices[counter])
                counter += 1
         
                # Always check that we haven't exhausted the elements in the clean_prices list
                if counter < n_elements:
                    price = clean_prices[counter]

            if price == 'PLD': 
                counter += 1
                all_prices[i_row, 3] = float(clean_prices[counter])
                counter += 1
                all_prices[i_row, 4] = float(clean_prices[counter])
                counter += 1
                all_prices[i_row, 5] = float(clean_prices[counter])
                counter += 1

                if counter < n_elements:
                    price = clean_prices[counter]

            if price == 'HP': 
                counter += 1
                all_prices[i_row, 6] = float(clean_prices[counter])
                counter += 1
                all_prices[i_row, 7] = float(clean_prices[counter])
                counter += 1
                all_prices[i_row, 8] = float(clean_prices[counter])
                counter += 1
            
                if counter < n_elements:
                    price = clean_prices[counter]

        # Initialize basic data structures
        columns = ['CardName', 'PriceNM', 'TradeNM', 'NumNM', 'PricePLD', 'TradePLD', 'NumPLD', 'PriceHP', 'TradeHP', 'NumHP']
        df = pd.DataFrame(columns=columns)
    
        try: 
            df['CardName'] = scrape_title

            for i, col in enumerate(columns[1:]):
                df[col] = all_prices[:,i]

        except ValueError:
            print(f'Error on page {page_num}, data table has likely an irregular format.')

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
    
    # Should we open the browser and show it or run it in the background
    show_browser = False

    # Should we use remote URL (on the internet) or local data previously downloaded
    remote = False

    # ABUgames main url
    url = 'https://abugames.com/buylist?fbclid=IwAR3gw3BG40HBl6LLSIksEhyyqYXW6q511u6LQ9Pt2J63yWBJaOHMyjfe-k4'
    #url = 'https://abugames.com/buylist/singles?search=mox'

    # Set the inital page to the final page that we want to analyze
    i_page = 1
    n_pages = 5

    # If remote make sure we are starting from the right page, so click on it and reload the content
    if remote:
        print('MTG Web scraper running remotely.')

        source, driver = get_page_source(url=url, show_browser=show_browser)
        xpath_str = '//button[contains(text(), "' + str(i_page) + '")]'
        driver.find_element_by_xpath(xpath_str).click() 
        time.sleep(10)
        source = driver.page_source
        
    # If not grabbing data from remote we will dump it all to csv files, which can be merged into a single dataframe
    else:
        full_data = pd.DataFrame()

        # Just set the source to None, we will reload it with beautiful soup
        print('MTG Web scraper running on local files.')
        source = None

    for i in range(i_page, n_pages+1):

        out_file = 'output/abugames_data_pag.' + str(i) + '.csv'
        data = scrape_titles_and_prices(source=source, page_num=i, remote=remote)

        # We need to click on the next page, that is, i+1
        xpath_str = '//button[contains(text(), "' + str(i+1) + '")]'

        # This is an alternative to keep in mind 
        #xpath_str = '//button[contains(text(), "NEXT")]'

        # Click on the page only if we did not 
        if remote:
            print(f'Page {i} saved to file {out_file}, going to page number: {i}')
            driver.find_element_by_xpath(xpath_str).click() 

            # Wait for some time after clicking on the link so that the page can load correctly
            time.sleep(10)

            # Get the new page source
            source = driver.page_source
        else:
            print(f'Saving dataframe to {out_file}. File header:')
            print(data.head(10))
            data.to_csv(out_file, index=False)

            if i == i_page:
                full_data = data.copy()
                print(i)
            else:
                full_data = pd.concat((full_data, data), axis=0, ignore_index=True)
                print('*', i)

    # Once we have ended looping on remote URLs we can close / quit everything 
    if remote:
        driver.close()
        driver.quit()

    # Print to a single dataframe
    else:
        str_num = str(i_page) + '-' + str(n_pages)
        out_file = 'output/abugames_all_data_' + str_num + '.csv'
        print(f'Printing full data to {out_file}')
        full_data.to_csv(out_file, index=False)

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

