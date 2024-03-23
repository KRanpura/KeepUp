from bs4 import BeautifulSoup
import requests

url = str("https://www.learndatasci.com/tutorials/ultimate-guide-web-scraping-w-python-requests-and-beautifulsoup/")
htmlPage = requests.get(url)
htmlGuts = BeautifulSoup(htmlPage.text)

for link in htmlGuts.find_all('a'):
    print(link.get('href'))