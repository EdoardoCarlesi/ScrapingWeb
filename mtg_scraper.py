import numpy as np
import pandas as pd
import requests
import time
import re
import os
import read_series as rs
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from selenium import webdriver
from selenium.webdriver.firefox.options import Options


def scrape_cardmarket(source=None, page_num=None, remote=True, cm_type=None): 
    """ Given a page source (ABUgames format!) we extract the card names and all the possible prices """

    # Basic paths and urls
    base_path = 'output/cardmarket_' + cm_type + '.'
    tmp_out = base_path + str(page_num) + '.html'

    # If reading a remote online page
    if remote:

        # Pass the source file extraced with Selenium 
        soup = BeautifulSoup(source, 'lxml')

        # We do some cleaning as well as a local html copy
        html = soup.prettify()  
        page_num = soup.find_all("span", {"class":"mx-1"})

        # Dump the clean version to a temporary output
        with open(tmp_out,"w") as out:
            for i in range(0, len(html)):
                try:
                    out.write(html[i])
                except Exception:
                    pass

        try:
            pn = re.search(' of \d', str(page_num)).group()[4:]
            return int(pn)
        except:
            print('Problem extracting page number, setting to default = 1')
            return 1

    # Read the output from a local source
    else:
        print(f'Extracting from local file: {tmp_out}')

        # Columns for the dataframe
        columns = []

        # Now read the cleaned up version of the file
        soup = BeautifulSoup(open(tmp_out, 'r'), 'lxml')

        # Once we have the page let's find all the card names
        scrape_title = [i.text.replace('\n', '').replace('  ', '')
                for i in soup.find_all("div", {"class":"col-10 col-md-8 px-2 flex-column align-items-start justify-content-center"})]

        # Remove element number zero, use it as column name
        columns.append(scrape_title[0])
        scrape_title.remove(scrape_title[0])

        # Initialize a numpy array to hold all the remaining data
        n_titles = len(scrape_title)
        clean_prices = np.zeros((n_titles, 5), dtype=float)

        # Scrape the Number columm
        scrape_number = [i.text.replace('\n', '').replace('  ', '')
                for i in soup.find_all("div", {"class":"col-md-2 d-none d-lg-flex has-content-centered"})]

        columns.append(scrape_number[0])
        scrape_number.remove(scrape_number[0])

        try:
            clean_prices[:, 0] = np.array(scrape_number)
        except ValueError:
            pass

        # Scrape the Available column
        scrape_available = [i.text.replace('\n', '').replace('  ', '')
                for i in soup.find_all("div", {"class":"col-availability px-2"})]

        columns.append(scrape_available[0])
        scrape_available.remove(scrape_available[0])
        clean_prices[:, 1] = np.array(scrape_available)

        # Scrape the From column
        scrape_from = [i.text.replace('\n', '').replace('  ', '').replace(',', '').replace(' ', '').replace('€', '').replace('N/A', '0').replace('.','')
                for i in soup.find_all("div", {"class":"col-price pr-sm-2"})]

        columns.append(scrape_from[0])
        scrape_from.remove(scrape_from[0])
        clean_prices[:, 2] = np.array(scrape_from)
        clean_prices[:, 2] /= 100.0

        # Scrape the avail foil
        scrape_avail_foil = [i.text.replace('\n', '').replace('  ', '').replace(',', '').replace(' ', '').replace('€', '')
                for i in soup.find_all("div", {"class":"col-availability d-none d-lg-flex"})]

        columns.append(scrape_avail_foil[0])
        scrape_avail_foil.remove(scrape_avail_foil[0])
        clean_prices[:, 3] = np.array(scrape_avail_foil)

        # Scrape the from foil
        scrape_from_foil = [i.text.replace('\n', '').replace('  ', '').replace(',', '').replace(' ', '').replace('€', '').replace('N/A', '0')
                for i in soup.find_all("div", {"class":"col-price d-none d-lg-flex pr-lg-2"})]

        columns.append(scrape_from_foil[0])
        scrape_from_foil.remove(scrape_from_foil[0])
        clean_prices[:, 4] = np.array(scrape_from_foil)

        data = pd.DataFrame(columns = columns)
        data[columns[0]] = scrape_title

        for i, col in enumerate(columns[1:]):
            data[col] = clean_prices[:, i]

        return data


def scrape_abugames(source=None, page_num=None, remote=True): 
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

        try:
            driver.get(url)
         
            # Wait for the page to load correctly
            print('Waiting for the page to load correctly...')
            time.sleep(time_sleep)

            # Once the page has been 
            source = driver.page_source
       
        except:
            print(f'Url {url} could not be reached')
            source = None
            driver = None

    return source, driver


def extract_cardmarket_weekly():
    """ This only works with the weekly top """

    url = 'https://www.cardmarket.com/en/Magic/Data/Weekly-Top-Cards'
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()
    webs = pd.read_html(webpage)
    webs[0].to_csv('output/cardmarket.csv')

    return webs[0]
    

def scrape_all_abugames(i_page=None, n_pages=None, remote=None, show_browser=None, verbose=False):
    """ This is a function that loops over all the pages and first dumpsto local html then extracts tables """

    # The basic url to start scraping from
    url = 'https://abugames.com/buylist?fbclid=IwAR3gw3BG40HBl6LLSIksEhyyqYXW6q511u6LQ9Pt2J63yWBJaOHMyjfe-k4'

    # If working remotely then we need to first get the data from the web
    if remote:

        # We need to skip some pages forward to reach for the inital page (i_page)
        count_page = 2
        skip = 2
        source, driver = get_page_source(url=url, show_browser=show_browser) 
        time.sleep(10)

        print(f'Skipping to page {count_page}')

        # Loop and move forward (click) until we reach the desired starting page
        while (count_page + skip < i_page):
            xpath_str = '//button[contains(text(), "' + str(count_page) + '")]'
            driver.find_element_by_xpath(xpath_str).click() 

            # We skip some pages to clikc to speedup
            count_page += skip

            print(f'Skipping to page {count_page}')

            # Wait some time but not too much, this one is pretty fast
            time.sleep(0.5)
            source = driver.page_source

    # Else, if we are not grabbing data from remote we will dump it all to csv files, which can be merged into a single dataframe
    else:
        full_data = pd.DataFrame()

        # Just set the source to None, we will reload it with beautiful soup
        print('MTG Web scraper running on local files.')
        source = None

    for i in range(i_page, n_pages+1):

        out_file = 'output/abugames_data_pag.' + str(i) + '.csv'
        data = scrape_abugames(source=source, page_num=i, remote=remote) 

        # We need to click on the next page, that is, i+1
        xpath_str = '//button[contains(text(), "' + str(i+1) + '")]'
        xpath_str_next = '//button[contains(text(), "NEXT")]'

        # Click on the page only if we did not 
        if remote:
            print(f'Page {i} saved to file {out_file}, going to page number: {i}')

            # This is clicking on NEXT simply...
            driver.find_element_by_xpath(xpath_str_next).click() 

            # Wait for some time after clicking on the link so that the page can load correctly
            time.sleep(5)

            # Get the new page source
            source = driver.page_source
        else:
            print(f'Saving dataframe to {out_file}. File header:')

            if verbose:
                print(data.head(10))

            data.to_csv(out_file, index=False)

            if i == i_page:
                full_data = data.copy()
                #print(i)
            else:
                full_data = pd.concat((full_data, data), axis=0, ignore_index=True)
                #print('*', i)

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

    
def scrape_all_cardmarket(remote=None, show_browser=None, cm_type=None, verbose=False):
    """ Loop over all cardmarket page and extract data """

    # Main cardmarket url
    #url_base = 'https://www.cardmarket.com/en/Magic/Products/Singles?site='; cm_type='std'

    # Cardmarket ordered by descending price, most expensive first
    url_base = 'https://www.cardmarket.com/en/Magic/Products/Singles?idCategory=1&idExpansion=0&idRarity=0&sortBy=price_desc&site='; cm_type='price_order'
    url_base_type = 'https://www.cardmarket.com/en/Magic/Products/Search?idCategory=0&idExpansion='; suffix_url='&idRarity=0&sortBy=price_desc&site='
    #https://www.cardmarket.com/en/Magic/Products/Search?idCategory=0&idExpansion=1269&idRarity=0&sortBy=price_desc&perSite=100
    #'https://www.cardmarket.com/en/Magic/Products/Search?idCategory=0&idExpansion=51&idRarity=0&sortBy=price_desc&site=2'
    local_url = 'output/cardmarket_price_order.' #1513.1.html'

    counter = 0
    series_ids = rs.return_series()

    if remote:

        # Get the total number of expansions
        for serie in series_ids:

            # First get the number of pages for this expansion
            serie = str(serie)
            url = url_base_type + serie + suffix_url + '1'
            source, driver = get_page_source(url=url, show_browser=show_browser)

            if source != None and driver != None:

                counter_str = serie + '.' + str(counter)
                n_pages = scrape_cardmarket(source=source, page_num=counter_str, remote=remote, cm_type=cm_type)
                print(f'Expansion {serie} has n_pages: {n_pages}')
                time.sleep(10)
                driver.close()

                # Loop on all the pages
                for counter in range(1, n_pages+1):
                    url = url_base + str(counter)
                    url = url_base_type + serie + suffix_url + str(counter)
                    check_url = local_url + str(serie) + '.' + str(counter) + '.html'
                    
                    if os.path.isfile(check_url):
                        print(f'Url {url} exists locally: {check_url}')
                    else:

                        print(f'Reading from {url}')
                        source, driver = get_page_source(url=url, show_browser=show_browser)
                        counter_str = serie + '.' + str(counter)
                        n_pages = scrape_cardmarket(source=source, page_num=counter_str, remote=remote, cm_type=cm_type)
                        time.sleep(10)
                        driver.close()
            
    # If not grabbing data from remote we will dump it all to csv files, which can be merged into a single dataframe
    else:
        print('MTG Web scraper running on local files.')

        full_data = pd.DataFrame()
        source = None

        # This is a loop on the local html files that extracted the information from the website
        for i in range(1, n_pages+1):
    
            # Name of the csv output
            out_file = 'output/cardmarket_data_pag.' + str(i) + '.csv'
            data = scrape_cardmarket(source=source, page_num=i, remote=remote, cm_type=cm_type)
    
            # Sanity check
            print(f'Saving dataframe to {out_file}. File header:')

            if verbose:
               print(data.head(10))

            data.to_csv(out_file, index=False)

            # Concatenate all the DataFrames into a single df
            if i == 1:
                full_data = data.copy()
            else:
                full_data = pd.concat((full_data, data), axis=0, ignore_index=True)

        # Print to a single dataframe
        str_num = str(i_page) + '-' + str(n_pages)
        out_file = 'output/cardmarket_all_data_' + str_num + '.csv'

        print(f'Printing full data to {out_file}')
        full_data.to_csv(out_file, index=False)


if __name__ == '__main__':
    """ Main wrapper """
    
    # Should we open the browser and show it or run it in the background
    show_browser = False

    # Should we use remote URL (on the internet) or local data previously downloaded
    remote = True

    # Set the inital page to the final page that we want to analyze
    i_page = 0
    n_pages = 6000

    #scrape_all_abugames(i_page=i_page, n_pages=n_pages, remote=remote, show_browser=show_browser, verbose=False)
    scrape_all_cardmarket(remote=remote, show_browser=show_browser, verbose=False)


