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
    urls = [
        'https://www.google.com/search?tbm=lcl&sxsrf=ALeKk00mjEPKdLuHIF69pewXC80KmlfwUA%3A1606921055223&ei=X6vHX971DIrA5OUP7rikqAk&hotel_occupancy=&q=alojamiento+puerto+rico+misiones&oq=alojamiento+puer&gs_l=psy-ab.3.0.35i39k1j0i67k1l2j0l7.484399.486313.0.487273.16.15.0.0.0.0.220.1986.0j12j2.14.0....0...1c.1.64.psy-ab..2.14.1980...46j0i433k1j46i433i131k1j46i433k1j46i67k1j0i433i131i67k1j0i20i263k1.0.T69IelvrPlY#rlfi=hd:;si:11749626320974400381,y,82SO0VBCrQs;mv:[[-26.809706799999997,-54.998407],[-26.8219182,-55.027229]]',
        'https://www.google.com/search?tbs=lf:1,lf_ui:9&tbm=lcl&sxsrf=ALeKk02d_99VcQiICEgnljlwgVEcpiloDg:1606930075482&q=restaurantes+puerto+rico+misiones&rflfq=1&num=10&sa=X&ved=2ahUKEwj9ts-C6a_tAhUSGLkGHZN2Cs8QjGp6BAgFEEs&biw=1366&bih=601#rlfi=hd:;si:;mv:[[-26.799132,-55.020778299999996],[-26.8239037,-55.032233399999996]];tbs:lrf:!1m4!1u3!2m2!3m1!1e1!1m4!1u2!2m2!2m1!1e1!2m1!1e2!2m1!1e3!3sIAE,lf:1,lf_ui:9',
        'https://www.google.com/search?biw=1366&bih=601&tbm=lcl&sxsrf=ALeKk03JVHC_f42WWM_5q1FUyPivFUkGdw%3A1606930082130&ei=os7HX529B_nB5OUP7JGgiAY&q=atracciones+puerto+rico+misiones&oq=atracciones+puerto+rico+misiones&gs_l=psy-ab.3..35i39k1.69904.71136.0.71611.11.9.0.0.0.0.298.1070.0j4j2.6.0....0...1c.1.64.psy-ab..8.1.297....0.NQF2feaXwos#rlfi=hd:;si:;mv:[[-26.7487985,-54.9150596],[-26.9348076,-55.0701689]];tbs:lrf:!1m4!1u3!2m2!3m1!1e1!1m4!1u2!2m2!2m1!1e1!2m1!1e2!2m1!1e3!3sIAE,lf:1,lf_ui:1',
        ]
    for url in urls:
        scrape_attractions(url)

    driver.close()


