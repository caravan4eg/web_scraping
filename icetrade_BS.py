import requests
import csv
from time import sleep
from random import uniform
from random import choice
from bs4 import BeautifulSoup
import params


def get_proxy():

    try:
        html = requests.get('https://free-proxy-list.net/').text
    except:
        print('Can not find proxy...')
        return None

    try:
        soup = BeautifulSoup(html, 'lxml')
        trs = soup.find('table', id='proxylisttable').find_all('tr')[1:20]
    except AttributeError as e:
        print(e)
        return None

    proxies = []
    for tr in trs:
        tds = tr.find_all('td')
        ip = tds[0].text.strip()
        port = tds[1].text.strip()

        schema = 'https' if 'yes' in tds[6].text.strip() else 'http'
        proxy = {'schema': schema, 'address': 'http://' + ip + ':' + port}
        proxies.append(proxy)
    p = choice(proxies)
    proxy = {p['schema']: p['address']}

    return proxy


def get_html(url, retry=3):
    headers = choice(params.headers)
    proxy = get_proxy()
    print('Choosen proxy: ', proxy)
    if proxy == None:
        print('Proxy could not be found')
    else:
        try:
            r = requests.get(url, headers=headers, proxies=proxy, timeout=5)
            print("Status: ", r.status_code)
            if r.status_code == 200:
                print(r.text)
                return r.text
            elif r.status_code != 200 and retry:
                print('We were spotted.\n I\'m sleeping for a while and after will restart...')
                sleep(uniform(3, 7))
                return get_html(url, retry-1)
            else:
                return None

        except:
            print("OOPS!! Connection Error. Technical Details given below:\n")
            sleep(uniform(3, 5))
            return None


def get_page_data(html):
    soup = BeautifulSoup(html, 'lxml')
    data = {}
    try:
        trs = soup.find('table', id='auctions-list').find_all('tr')[1:]
    except:
        return data
    for tr in trs:
        tds = tr.find_all('td')

        try:
            descr = tds[0].text.strip()
        except:
            descr = ''

        try:
            url = tds[0].find('a').get('href')
        except:
            url = ''

        try:
            name = tds[1].text.strip()
        except:
            name = ''

        try:
            country = tds[2].text.strip()
        except:
            country = ''

        try:
            number = tds[3].text.strip()
        except:
            number = ''

        try:
            price = tds[4].text.strip()
        except:
            price = ''

        try:
            deadline = tds[5].text.strip()
        except:
            deadline = ''

        data = {'descr': descr,
                'url': url,
                'name': name,
                'country': country,
                'number': number,
                'price': price,
                'deadline': deadline
                }
        print(data)
        write_csv(data)


def write_csv(data):
    with open(params.file_csv, 'a') as f:
        order = ['number', 'name', 'descr', 'country', 'price', 'deadline', 'url']
        writer = csv.DictWriter(f, fieldnames=order)
        writer.writerow(data)


def main():

    for i in range(1, 2):  # 64
        url = params.url_pattern.format(str(i))

        print('Getting info. Page: ', i)

        html = get_html(url)
        sleep(uniform(5, 10))
        if html:
            get_page_data(html)

        else:
            sleep(uniform(0.1, 1))


if __name__ == '__main__':
    main()
