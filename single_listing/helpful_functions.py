import csv
from enum import unique
from os import link


def cleanFileData(ur_list):
    r = []
    for l in ur_list:
        r.append(l.strip('\n'))
    return r


def clean_pid_csv(url_pids):
    csv_pids = csv.reader(url_pids)
    the_goods = {}
    found_pids = []
    for link in csv_pids:
        if link[0] != 'link':
            if link[1] != ' [no listings here]':
                if link[1] not in found_pids:
                    found_pids.append(link[1])
                    try:
                        the_goods[link[0]].append(link[1])
                    except:
                        the_goods[link[0]] = [link[1]]
    return the_goods


def get_base_url(url):
    key = '/'
    l = 0
    base_url = ''
    for c in url:
        if c == key:
            l += 1
            if l == 3:
                break
        base_url += c
    return base_url


def get_num_listings(x):
    return None if x[:1] == '\n' else x


def get_price(x):
    if x:
        return x.replace('$', '')
    else:
        return None


def is_listings(response):
    if response.xpath('//span[@class="totalcount"]/text()').get():
        return True
    else:
        return False
