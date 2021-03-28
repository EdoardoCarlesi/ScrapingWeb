import numpy as np
import pandas as pd
import tkinter as tk
import read_series as rs
import requests
import time
import re
import os
import logging
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from selenium import webdriver
from selenium.webdriver.firefox.options import Options


# Logging settings
log_filename = 'logfile.log'
logging.basicConfig(filename=log_filename,level=logging.INFO) 
logging.info('Logfile for MTG Scraper...\n')

global system_type
global output_folder 
global run_mode 
global settings

system_type = 'LINUX'
output_folder = 'output/'
run_mode = 'remote'


def read_settings():
    """ Read the program settings from the .csv file """

    settings_file = 'settings.csv'

    try:
        settings = pd.read_csv(settings_file)
    except:
        logging.info('File not found: ' + settings_file)
        exit()

    if settings['system_type'].values == 'LINUX':
        logging.info('Using LINUX default settings.')

    elif settings['system_type'].values == 'WINDOWS':
        logging.info('Using WINDOWS settings.')
        output_folder = 'output\\'

    else:
        logging.info('Error in the settings.csv file for the system_type option.')
        exit()

    return settings


def return_series():
    """ Read the series codes from a .txt file """

    years = [ 1990 + i for i in range(0, 34)]

    series_file='series_names_ids.txt'

    try:
        tags_file = open(series_file, 'r')
    except:
        logging.info('Expansion tag files not found: ' + series_file)

    all_nums = []
    number = []
    nstr = ''

    while (nstr != '3500'):
          
        # read by character
        char = tags_file.read(1)          
        if char == '"':
         
            if len(number) > 0:
                nstr = ''.join(number)
                #print(nstr)
                all_nums.append(int(nstr))

            number = []

        if char.isdigit():
            number.append(char)
    
    all_nums = set(all_nums)

    for yr in years:
        if (yr in all_nums):
            all_nums.remove(yr)

    all_nums = list(all_nums)
    all_nums.sort()

    return all_nums



def scrape_cardmarket(source=None, page_num=None, series=None, remote=True, cm_type=None): 
    """ Given a page source (ABUgames format!) we extract the card names and all the possible prices """

    # Basic paths and urls
    base_path = output_folder + 'cardmarket_' + cm_type + '.' 
    tmp_out = base_path + str(series) + '.' + str(page_num) + '.html'

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
            msg='Problem extracting page number, setting to default = 1'
            logging.info(msg)
            print(msg)
            return 1

    # Read the output from a local source
    else:
        msg='Extracting from local file: ' + tmp_out
        print(msg)

        # Columns for the dataframe
        columns = []

        # Now read the cleaned up version of the file
        soup = BeautifulSoup(open(tmp_out, 'r'), 'lxml')

        # Once we have the page let's find all the card names
        scrape_title = [i.text.replace('\n', '').replace('  ', '')
                #for i in soup.find_all("div", {"class":"col-10 col-md-8 px-2 flex-column align-items-start justify-content-center"})]
                for i in soup.find_all("div", {"class":""})]    #FIXME

        if len(scrape_title) > 0:

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
        else:

            return None


def scrape_abugames(source=None, page_num=None, remote=True): 
    """ Given a page source (ABUgames format!) we extract the card names and all the possible prices """

    # Basic paths and urls
    base_path = output_folder + 'abugames.'
    tmp_out = base_path + str(page_num) + '.html'

    # If reading a remote online page
    if remote:

        # Pass the source file extraced with Selenium 
        soup = BeautifulSoup(source, 'lxml')

        # We do some cleaning as well as a local html copy
        html = soup.prettify()  

        msg = 'Exporting to ' + tmp_out
        logging.info(msg)
        print(msg)

        # Dump the clean version to a temporary output
        with open(tmp_out,"w") as out:
            for i in range(0, len(html)):
                try:
                    out.write(html[i])
                except Exception:
                    pass

    # Read the output from a local source
    else:
        msg='Extracting from local file: ' + tmp_out
        logging.info(msg)
        print(msg)

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

            if price == 'NM': 
                counter += 1
                all_prices[i_row, 0] = float(clean_prices[counter])
                counter += 1
                all_prices[i_row, 1] = float(clean_prices[counter])
                counter += 1

                try:
                    all_prices[i_row, 2] = float(clean_prices[counter])
                except:
                    all_prices[i_row, 2] = 0.0 

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
                try:
                    all_prices[i_row, 6] = float(clean_prices[counter])
                    counter += 1
                    all_prices[i_row, 7] = float(clean_prices[counter])
                    counter += 1
                    all_prices[i_row, 8] = float(clean_prices[counter])
                    counter += 1

                except:
                    all_prices[i_row, 6] = 0
                    counter += 1
                    all_prices[i_row, 7] = 0
                    counter += 1
                    all_prices[i_row, 8] = 0
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
            msg = 'Error on page %d, data table has likely an irregular format.' % page_num
            logging.info(msg)
            print(msg) 

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
            msg='Waiting for the page to load correctly...'
            logging.info(msg)
            print('Waiting for the page to load correctly...')
            time.sleep(time_sleep)

            # Once the page has been 
            source = driver.page_source
       
        except:
            msg = 'Url %s could not be reached' % url
            logging.info(msg)
            print(msg) 
            source = None
            driver = None

    return source, driver


def extract_cardmarket_weekly():
    """ This only works with the weekly top """

    url = 'https://www.cardmarket.com/en/Magic/Data/Weekly-Top-Cards'
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()
    webs = pd.read_html(webpage)
    webs[0].to_csv(output_folder + 'cardmarket.csv')

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

        msg = 'Skipping to page %d' % count_page
        logging.info(msg)
        print(msg) 

        # Loop and move forward (click) until we reach the desired starting page
        while (count_page + skip < i_page):
            xpath_str = '//button[contains(text(), "' + str(count_page) + '")]'
            driver.find_element_by_xpath(xpath_str).click() 

            # We skip some pages to clikc to speedup
            count_page += skip

            msg = 'Skipping to page %d' % count_page 
            logging.info(msg)
            print(msg) 

            # Wait some time but not too much, this one is pretty fast
            time.sleep(0.5)
            source = driver.page_source

    # Else, if we are not grabbing data from remote we will dump it all to csv files, which can be merged into a single dataframe
    else:
        full_data = pd.DataFrame()

        # Just set the source to None, we will reload it with beautiful soup
        msg = 'MTG Web scraper running on local files.'
        logging.info(msg)
        print(msg)
        source = None

    for i in range(i_page, n_pages+1):

        out_file = output_folder + 'abugames_data_pag.' + str(i) + '.csv'
        data = scrape_abugames(source=source, page_num=i, remote=remote) 

        # We need to click on the next page, that is, i+1
        xpath_str = '//button[contains(text(), "' + str(i+1) + '")]'
        xpath_str_next = '//button[contains(text(), "NEXT")]'

        # Click on the page only if we did not 
        if remote:
            msg = 'Page %d saved to file %d, going to page number: %d' % (i, out_file, i)
            logging.info(msg)
            print(msg)

            # This is clicking on NEXT simply...
            driver.find_element_by_xpath(xpath_str_next).click() 

            # Wait for some time after clicking on the link so that the page can load correctly
            time.sleep(5)

            # Get the new page source
            source = driver.page_source
        else:
            msg = 'Saving dataframe to %s. File header:' % out_file
            logging.info(msg)
            logging.info(data.head())
            print(msg)

            if verbose:
                print(data.head(10))

            data.to_csv(out_file, index=False)

    # Once we have ended looping on remote URLs we can close / quit everything 
    if remote:
        driver.close()
        driver.quit()
    
    
def scrape_all_cardmarket(exp_code=None, remote=None, show_browser=None, cm_type=None, verbose=False):
    """ Loop over all cardmarket page and extract data """

    # Main cardmarket url
    #url_base = 'https://www.cardmarket.com/en/Magic/Products/Singles?site='; cm_type='std'

    # Cardmarket ordered by descending price, most expensive first
    url_base = 'https://www.cardmarket.com/en/Magic/Products/Singles?idCategory=1&idExpansion=0&idRarity=0&sortBy=price_desc&site='; cm_type='price_order'
    url_base_type = 'https://www.cardmarket.com/en/Magic/Products/Search?idCategory=0&idExpansion='; suffix_url='&idRarity=0&sortBy=price_desc&site='
    #https://www.cardmarket.com/en/Magic/Products/Search?idCategory=0&idExpansion=1269&idRarity=0&sortBy=price_desc&perSite=100
    #https://www.cardmarket.com/en/Magic/Products/Search?idCategory=0&idExpansion=51&idRarity=0&sortBy=price_desc&site=2
    local_url = output_folder + 'cardmarket_price_order.'

    counter = 0
    series_ids = rs.return_series()

    if exp_code == None:
        ind_serie = 0
    else:
        ind = 0
        for i, serie in enumerate(series_ids):
            if int(serie) == int(exp_code):
                ind = i

    if remote:

        # Get the total number of expansions
        for serie in series_ids[ind_serie:]:
            # First get the number of pages for this expansion
            serie = str(serie)
            url = url_base_type + serie + suffix_url + '1'
            source, driver = get_page_source(url=url, show_browser=show_browser)

            if source != None and driver != None:

                counter_str = serie + '.' + str(counter)
                n_pages = scrape_cardmarket(source=source, series=serie, page_num=counter_str, remote=remote, cm_type=cm_type)
                msg = 'Expansion %s has n_pages: %d pages' % (series, n_pages)
                logging.info(msg)
                print(msg)
                time.sleep(10)
                driver.close()

                # Loop on all the pages
                for counter in range(1, n_pages+1):
                    url = url_base + str(counter)
                    url = url_base_type + serie + suffix_url + str(counter)
                    check_url = local_url + str(serie) + '.' + str(counter) + '.html'
                    
                    if os.path.isfile(check_url):
                        msg = 'Url exists locally: ' % (url, check_url)
                        print(f'Url {url} exists locally: {check_url}')
                    else:

                        msg = 'Reading from %s' % url
                        source, driver = get_page_source(url=url, show_browser=show_browser)
                        counter_str = serie + '.' + str(counter)
                        n_pages = scrape_cardmarket(source=source, series=serie, page_num=counter_str, remote=remote, cm_type=cm_type)
                        time.sleep(10)
                        driver.close()
            
    # If not grabbing data from remote we will dump it all to csv files, which can be merged into a single dataframe
    else:
        print('MTG Web scraper running on local files.')

        full_data = pd.DataFrame()
        source = None
        n_pages = 2000

        for serie in series_ids:

            # This is a loop on the local html files that extracted the information from the website
            for i in range(1, n_pages+1):
        
                # Name of the csv output
                out_file = output_folder + 'cardmarket_data_pag.' + str(serie) + '.' + str(i) + '.csv'
                url_file = local_url + str(serie) + '.' + str(i) + '.html'

                # check out that this file exists
                if os.path.isfile(url_file):
                    #source, driver = get_page_source(url=url_file, show_browser=show_browser)
                    data = scrape_cardmarket(source=source, page_num=i, series=serie, remote=remote, cm_type=cm_type) 
            
                    # Sanity check

                    if verbose:
                       print(data.head(10))
    
                    if data != None:
                        print(f'Saving dataframe to {out_file}. File header:')
                        data.to_csv(out_file, index=False)
                    

def merge_all_abugames(i_ini=1, i_end=5122, f_out=output_folder+'abugames_completo.csv'):
    """ Dump all the files to the same CSV """

    file_root=output_folder+'abugames_'
    this_abugames = file_root + '1.csv'
    full_data = pd.read_csv(this_abugames)

    for i in range(i_ini+1, i_end):
        this_abugames = file_root + str(i) + '.csv'
        data = pd.read_csv(this_abugames)
        full_data = pd.concat((full_data, data), axis=0, ignore_index=True)

    print('Merging all files to {f_out}')
    full_data.to_csv(f_out)


def merge_all_cardmarket(i_ini=1, i_max=200, f_out=output_folder+'cardmarket_completo.csv'):
    """ Dump all the files to the same CSV """

    file_root=output_folder+'cardmarket_'
    this_cardmarket = file_root + '1.1.csv'
    full_data = pd.read_csv(this_cardmarket)
    series_ids = rs.return_series()

    # Loop on the expansions
    for serie in series_ids:

        # Loop on the assumed max number of pages per expansion
        for i in range(i_ini+1, i_end):
            this_cardmarket = file_root + str(serie) + '.' + str(i) + '.csv'

            # Read only if file exists
            if os.path.isfile(this_cardmarket):
                data = pd.read_csv(this_cardmarket)
                full_data = pd.concat((full_data, data), axis=0, ignore_index=True)

    print('Merging all files to {f_out}')
    full_data.to_csv(f_out)



if __name__ == '__main__':
    """ Main wrapper """
     
    settings = read_settings()

    '''
    root= tk.Tk()
    canvas1 = tk.Canvas(root, width = 300, height = 300)
    canvas1.pack()

    def hello ():  
        label1 = tk.Label(root, text= 'Hello World!', fg='green', font=('helvetica', 12, 'bold'))
        canvas1.create_window(150, 200, window=label1)
        
    button1 = tk.Button(text='Click Me',command=hello, bg='brown',fg='white')
    canvas1.create_window(150, 150, window=button1)
    root.mainloop()
    '''

    # Should we open the browser and show it or run it in the background
    show_browser = False

    # Should we use remote URL (on the internet) or local data previously downloaded
    if settings['scrape_type'].values == 'remote':
        msg = 'Running in online mode'
        remote = True

    elif settings['scrape_type'].values == 'offline':
        msg = 'Running offline in local mode'
        remote = False

    else:
        msg = 'Error. Could not find correct setting type for scrape_type'
        exit()

    logging.info(msg)
    print(msg)

    if settings['site'].values == 'abugames':
        # Set the inital page to the final page that we want to analyze
        i_page = int(settings['init_page'].values)
        end_page = int(settings['end_page'].values)
        msg = 'Running for abugames from page %d to %d' % (i_page, end_page)
        print(msg)
        logging.info(msg)

        scrape_all_abugames(i_page=i_page, n_pages=end_page, remote=remote, show_browser=show_browser, verbose=False)

        if settings['scrape_type'].values == 'offline':
            msg = 'Merging all abugames files into one'
            merge_all_abugames(i_ini=i_page, i_end=end_page, f_out=output_folder+'abugames_completo.csv')
            print(msg)
            logging.info(msg)

    elif settings['site'].values == 'cardmarket':
        exp_code = int(settings['expansion_code'].values)
        msg = 'Running for cardmarket from page %d' % (exp_code)
        print(msg)
        logging.info(msg)

        scrape_all_cardmarket(remote=remote, show_browser=show_browser, verbose=False)

        if settings['scrape_type'].values == 'offline':
            msg = 'Merging all abugames files into one'
            merge_all_abugames(i_ini=i_page, i_end=end_page, f_out=output_folder+'abugames_completo.csv')
            print(msg)
            logging.info(msg)

    else:
        msg = 'Could not find correct setting type for site type'
        print(msg)
        logging.info(msg)
        exit()


    



