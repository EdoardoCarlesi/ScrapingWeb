import time
from selenium import webdriver
from bs4 import BeautifulSoup


def site_login(url=None):

    driver.get(url)
    driver.find_element_by_name("loginform").send_keys("THISISMYEMAIL")
    driver.find_element_by_name("pwd").send_keys("THISISMYPASSWORD")
    driver.find_element_by_xpath('/html/body/section[1]/div/div/div/div[2]/header/a').click()



driver = webdriver.Firefox()
url = 'http://sdsclub.com/login'
#url = 'http://www.google.com'
#url = 'https://abugames.com/buylist?fbclid=IwAR3gw3BG40HBl6LLSIksEhyyqYXW6q511u6LQ9Pt2J63yWBJaOHMyjfe-k4'
driver.get(url)
time.sleep(5)

site_login(url=url)

#driver.find_element_by_xpath('/html/body/section[1]/div/div/div/div[2]/header/a').click()
#driver.find_element_by_id("username")
#driver.find_element_by_id("password")

time.sleep(5)
driver.quit()





