import pandas as pd
from urllib.request import Request, urlopen
import requests
from bs4 import BeautifulSoup

#url = 'https://abugames.com/buylist?fbclid=IwAR3gw3BG40HBl6LLSIksEhyyqYXW6q511u6LQ9Pt2J63yWBJaOHMyjfe-k4'
url = 'https://www.cardmarket.com/en/Magic/Data/Weekly-Top-Cards'

req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
webpage = urlopen(req).read()
webs = pd.read_html(webpage)

print(type(webs[0]))

print(webs[0].to_csv('/home/edoardo/cardmarket.csv'))

print(webs)
'''

page = requests.get(url)


print(page.content)

soup = BeautifulSoup(page.content, 'html.parser')

print(soup.prettify())

'''

