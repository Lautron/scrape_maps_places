from selenium import webdriver
from bs4 import BeautifulSoup
import re, csv
import time
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
import random

chrome_options = Options()
chrome_options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36")
driver = webdriver.Chrome(options=chrome_options)


def write_csv(res_list):
    with open('results.csv', 'a') as f:
        writer = csv.writer(f)
        for dicty in res_list:
            writer.writerow([dicty['name'], dicty['direction'], dicty['phone'], dicty['name'] if random.choice([True, False]) else '', dicty['website'], dicty['latitude'], dicty['longitude'], dicty['ptype']])
#Parse page
def parse_page(ptype):
    items = driver.find_elements_by_class_name("VkpGBb")
    res_list = []
    for item in items:
        item.click()
        time.sleep(1)
        element = WebDriverWait(driver, 60).until( 
            EC.presence_of_element_located((By.CLASS_NAME, "ifM9O")) 
        )
        html = driver.find_element_by_class_name("ifM9O").get_attribute("innerHTML")
        place_dict = parse_html(html)

        try:
            link_with_coord = driver.find_element_by_xpath('//*[@id="lu_pinned_rhs"]/div/div/div[1]/div/div/div[14]/div[4]/div[2]/a').get_attribute('href')
        except:
            link_with_coord = ''
            
        mo = re.search(r'@(.*),(.*),', link_with_coord)
        lat, long = mo.groups() if link_with_coord else [None, None]

        place_dict.update({'latitude': lat, 'longitude': long, 'ptype': ptype})
        res_list.append(place_dict)
        print(', '.join([i for i in place_dict.values() if i]), '\n')
    return res_list

def clean_string(string):
    string_list = string.replace('\n', '').split(' ')
    exclude = {'Llegar', 'Guardado', '(0)', 'Guardar',}
    return ' '.join([word for word in string_list if word and word not in exclude]).title()

def parse_html(html):
    soup = BeautifulSoup(html, 'lxml')
    name = soup.find('div', class_='SPZz6b').find('span').text

    try:  
        direction = soup.find('span', class_='LrzXr').text
    except:
        direction = None

    try:
        phone = soup.find('span', class_='LrzXr zdqRlf kno-fv').text
    except:
        phone = None

    website = soup.find('div', class_='QqG1Sd').find('a').get('href')
    return {
        'name': clean_string(name),
        'direction': clean_string(direction),
        'phone': phone,
        'website': website if website != '#' else '',
    }

def scrape_attractions(urls):
    driver.get(url)
    ptype = ''
    for category in ['alojamiento', 'atraccion', 'restaurante']:
        if category in url:
            ptype = category
            break

    if not ptype:
        print('Invalid category')
        return
    time.sleep(5)
    data = parse_page(ptype)
    write_csv(data)


if __name__ == "__main__":
    urls = []
    for url in urls:
        scrape_attractions(url)

    driver.close()


