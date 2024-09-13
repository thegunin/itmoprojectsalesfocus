import requests
import concurrent.futures
from bs4 import BeautifulSoup

URL = "https://zachestnyibiznes.ru/company/ul/1027804877616_7810148720_OOO-ELMA"

def fetch_url(session, thread_num):
    response = session.get(URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    website_elements = soup.find_all('div')
    for element in website_elements:
        website = element.text.strip()
        print(f"Thread {thread_num}: Website: {website}")

def main():
    with requests.Session() as session:
        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
            futures = [executor.submit(fetch_url, session, i) for i in range(100)]
            concurrent.futures.wait(futures)

if __name__ == "__main__":
    main()