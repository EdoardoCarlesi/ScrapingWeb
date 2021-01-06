import requests

from bs4 import BeautifulSoup

#url = 'https://google.com'
url = 'http://www.darklyrics.com/n/nanowar.html'
#url = 'http://www.darklyrics.com/lyrics/nanowar/truemetaloftheworld.html'
r = requests.get(url)

print(r.status_code)
print(r.headers['content-type'])
print(r.encoding)
#print(r.text)

soup = BeautifulSoup(r.content, 'lxml')

print(soup.title.text)
#print(soup.get_text())
print(soup.find_all('a'))
#print(soup.prettify())
#print(soup.title.parent.name)

#albums = soup.find_all("div", class_="album")

#for album in albums:
#    print(album.text)

