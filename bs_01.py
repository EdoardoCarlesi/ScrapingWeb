import pandas 
import requests
import time
from bs4 import BeautifulSoup

#print(r.headers['content-type'])
#print(r.encoding)
#print(r.text)


def review_count_scrape():
    url = 'https://www.amazon.com/Best-Sellers/zgbs'
    headers = ({'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'})

    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.content, 'lxml')

    n_reviews = [i.text for i in soup.find_all('a', {'class': 'a-size-small a-link-normal'})]
    print(n_reviews)
    #time.sleep(10)

def youtube_views_scrape():
    url = 'https://www.amazon.com/Best-Sellers/zgbs'
    headers = ({'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'})

    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.content, 'lxml')
    #print(soup.find_all('yt-formatted-string'))
    #print(soup.find_all('yt-view-count-renderer'))
    print(soup.prettify())
    
    #n_views = [i.text for i in soup.find_all('yt-formatted-string')]
    
    #print(n_views)


youtube_views_scrape()

#review_count_scrape()


#print(soup.title.text)
#print(soup.get_text())
#print(soup.prettify())
#print(soup.title.parent.name)

#albums = soup.find_all("div", class_="album")

#for album in albums:
#    print(album.text)

