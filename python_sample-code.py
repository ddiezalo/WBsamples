''' 
    This was one of the scripts I used to scrape data from various online supermarkets in Spain.

	Created by Daniel Díez Alonso, all rights reserved.
    Shared only for recruitment purposes. Please, do not circulate for any other purposes.
'''
#! /usr/bin/env python

import urllib3.request
import os, json, pandas
import requests
from bs4 import BeautifulSoup
from time import sleep
import time
import random
from lxml import html
import numpy as np
import html2text
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

# disable urllib3 warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def AmazonCodes(cat, amid):
    categ = ((cat=="water")*"6347510031" + (cat=="fizzy")*"6347561031" + (cat=="teas")*"6347570031" + (cat=="vegs")*"6349935031"
        + (cat=="juice")*"21902138031" + (cat=="choco")*"6347532031") + (cat=="sports")*"6347523031"
    cookies = 'session-id=%s, other parts = other parts' % amid
    headers = {'Cookie': cookies, "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
               "Accept-Encoding":"gzip, deflate", "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
               "DNT":"1","Connection":"close", "Upgrade-Insecure-Requests":"1"}
    for n in range (1,3):
        print('Processing Amazon page ' + str(n) + ' for ' + cat)
        sleep(1)
        if n==1:
            url = "https://www.amazon.es/gp/bestsellers/grocery/" + categ
        else:
            url = "https://www.amazon.es/gp/bestsellers/grocery/%s/ref=zg_bs_pg_%s?ie=UTF8&pg=%s" % (categ,str(n),str(n))
        print(url)
        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.content, features="lxml")
        doc = soup.find_all('li', class_='zg-item-immersion')
        print(len(doc),' products')
        for items in range(0, len(doc)):
            prod = doc[items]
            try:
                RAW_RANK = prod.find('span', class_='zg-badge-text')
                RAW_CODE = prod.find('a', class_='a-link-normal').get('href')
                RAW_NAME = prod.find('div', class_='p13n-sc-truncate-desktop-type2')
                RAW_PRICE = prod.find('span', class_='p13n-sc-price')
                RAW_DEAL = prod.find('span', class_='a-color-secondary')
                RAW_STARS = prod.find('span', class_='a-icon-alt')
                RAW_REVS = prod.find('a', class_='a-size-small a-link-normal')
            except AttributeError as e:
                return None

            RANK = RAW_RANK.get_text() if RAW_RANK else None
            temp1 = RAW_CODE.find('/dp/') + 4
            temp2 = RAW_CODE.find('/ref=') if RAW_CODE.find('/ref=') else len(RAW_CODE)
            CODE = RAW_CODE[temp1:temp2]
            NAME = ' '.join(''.join(RAW_NAME.get_text()).split()) if RAW_NAME else None
            PRICE = ' '.join(''.join(RAW_PRICE.get_text()).split()).strip() if RAW_PRICE else None
            PRICE = PRICE.replace(',','.') if RAW_PRICE else None
            DEAL = RAW_DEAL.get_text() if RAW_DEAL else None
            temp1 = RAW_STARS.get_text() if RAW_STARS else ''
            temp2 = temp1.find(' de')
            STARS = temp1[0:temp2].replace(',','.')
            REVS =  ' '.join(''.join(RAW_REVS.get_text()).split()) if RAW_REVS else None

            if page.status_code != 200:
                raise ValueError('captha')

            data = {
                'RANK': RANK,
                'CODE': CODE,
                'NAME': NAME,
                'PRICE': PRICE,
                'DEAL': DEAL,
                'STARS': STARS,
                'REVIEWS': REVS,
                'CATEGORY': cat,
                'PUM': '',
            }
            itemlist.append(CODE)
            extracted1.append(data)

def AmazonParser(code, cat, amid):
    cookies = 'session-id=%s, other parts = other parts' % amid
    headers = {'Cookie': cookies, "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
               "Accept-Encoding":"gzip, deflate", "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
               "DNT":"1","Connection":"close", "Upgrade-Insecure-Requests":"1"}
    sleep(1)
    print('Processing Amazon item ' + code + ' in ' + cat)
    url = "https://www.amazon.es/dp/" + code
    print(url)
    page = requests.get(url, headers=headers)
    doc = BeautifulSoup(page.content, features="lxml")
    try:
        RAW_PRICE = doc.find('span', id='price_inside_buybox')
        RAW_SHIP = doc.find('span', id='price-shipping-message')
        RAW_SELLER = doc.find('div', id='merchant-info')
        RAW_BRAND= None
        RAW_MANUF = None
        RAW_VOLUME = None
        RAW_RANK = None
        doc2 = doc.find('div', id='prodDetails').find_all('tr')
        for x in range(0,len(doc2)):
            temp = doc2[x].find('th').get_text()
            if temp.find('Marca')>0:
                RAW_BRAND = doc2[x].find('td').get_text()
            if temp.find('Fabricante')>0:
                RAW_MANUF = doc2[x].find('td').get_text()
            if temp.find('Volumen')>0:
                RAW_VOLUME = doc2[x].find('td').get_text()
            if temp.find('Clasificación')>0:
                RAW_RANK = doc2[x].find('td').get_text()
    except AttributeError as e:
        return None

    RANK = ' '.join(''.join(RAW_RANK).split()) if RAW_RANK else None
    PRICE = ' '.join(''.join(RAW_PRICE.get_text()).split()) if RAW_PRICE else None
    PRICE = PRICE.replace(',','.') if RAW_PRICE else None
    SHIP = ' '.join(''.join(RAW_SHIP.get_text()).split()) if RAW_SHIP else None
    SHIP = SHIP.replace(',','.') if RAW_SHIP else None
    SELLER = ' '.join(''.join(RAW_SELLER.get_text()).split()) if RAW_SELLER else None
    BRAND = ' '.join(''.join(RAW_BRAND).split()) if RAW_BRAND else None
    MANUF = ' '.join(''.join(RAW_MANUF).split()) if RAW_MANUF else None
    VOLUME = ' '.join(''.join(RAW_VOLUME).split()) if RAW_VOLUME else None
    VOLUME = VOLUME.replace(',','.') if RAW_VOLUME else None

    if page.status_code != 200:
        raise ValueError('captha')

    data = {
        'CODE': code,
        'RANK2': RANK,
        'PRICE2': PRICE,
        'SHIPPING': SHIP,
        'SELLER': SELLER,
        'BRAND': BRAND,
        'MANUFACTURER': MANUF,
        'VOLUME': VOLUME
    }
    extracted2.append(data)

def EroskiParser(cat):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}
    section = (cat=='water')*"2060211-bebidas/2060212-agua/" + (cat=='juice')*"2060211-bebidas/2060243-zumos-y-nectar/" + (cat=='fizzy')*"2060211-bebidas/2060219-refrescos/" + \
              (cat=='vegs')*"2059807-leche-batidos-y-bebidas-vegetales/2059814-bebida-de-soja-y-otros-cereales" + (cat=='beer')*"2060211-bebidas/2060233-cervezas"
    url = "https://supermercado.eroski.es/es/supermercado/" + section
    # Scroll down to load full list of items (several pages)
    firefox_profile = webdriver.FirefoxProfile()
    firefox_profile.set_preference('permissions.default.image', 2)
    firefox_profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')
    driver = webdriver.Firefox(firefox_profile=firefox_profile)
    driver.get(url)
    lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
    match = False
    while (match == False):
        lastCount = lenOfPage
        time.sleep(3)
        lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        if lastCount == lenOfPage:
            match = True
    sleep(3)
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    # os.system('tskill plugin-container')
    driver.quit()

    # Identify items and start scraping
    doc = soup.find_all('div', class_='product-description')
    print('collecting ', len(doc), ' products')
    for items in range (0,len(doc)):
        prod=doc[items]
        RAW_NAME = prod.find('h2', class_='product-title product-title-resp')
        RAW_CODE = prod.find('a').get('href')
        temp1 = RAW_CODE.find('detail/') +7 if RAW_CODE else 0
        temp2 = RAW_CODE[temp1:].find('-') + temp1  if RAW_CODE else 0
        RAW_PRICE = prod.find('span', class_='price-now')
        RAW_PUM = prod.find('span', class_='price-product')
        RAW_BEFORE = prod.find('span', class_='price-offer-before')
        RAW_DEAL = prod.find('div', class_='product-offer-yellow')
        RAW_STARS = prod.find_all('div', class_='star checked')
        RAW_REVS = prod.find('div', class_='starbar')

        NAME = ' '.join(''.join(RAW_NAME.get_text()).split()) if RAW_NAME else None
        CODE = RAW_CODE[temp1:temp2] if RAW_CODE else None
        PRICE = ' '.join(''.join(html2text.html2text(str(RAW_PRICE))).split()).strip() if RAW_PRICE else None
        PUM = ' '.join(''.join(RAW_PUM.get_text()).split()) if RAW_PUM else None
        POLD = ' '.join(''.join(RAW_BEFORE.get_text()).split()) if RAW_BEFORE else None
        DEAL = ' '.join(''.join(RAW_DEAL.get_text()).split()) if RAW_DEAL else None
        STARS = len(RAW_STARS) if RAW_STARS else 0
        REVS = RAW_REVS.get_text() if RAW_REVS else None

        data = {
            'NAME': NAME,
            'CODE': CODE,
            'PRICE': PRICE,
            'BRAND': '',
            'PUM': PUM,
            'POLD': POLD,
            'CATEGORY': cat,
            'SELLER': 'Eroski',
            'REVIEWS': REVS,
            'STARS': STARS,
            'PRICE2': '',
            'SHIPPING': '',
            'MANUFACTURER': '',
            'VOLUME': '',
            'RANK': '',
            'DEAL': DEAL,
        }
        extracted_data.append(data)

def CarrefourParser(cat):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}
    section= (cat=='water1')*"N-17mh7wf/c" + (cat=='water2')*"N-18bnwb8/c" + (cat=='water3')*"N-iphdvi/c" + (cat=='water4')*"N-f33m9a/c" + \
             (cat=='juice1')*"N-szavff/c" + (cat=='juice2')*"N-1dqrqt0/c" + (cat=='beer')*"N-1uq8b5u/c" + (cat=='cola')*"N-16p62qc/c" + \
             (cat=='fizzy')*"N-17xth7w/c" + (cat=='sport')*"N-1uhehvr/c" + (cat=='tonic')*"N-p90ax4/c" + (cat=='teas')*"N-dvfqwt/c" + \
             (cat=='energy')*"N-1e7r1yb/c" + (cat=='vegs')*"N-alav3p/c" + (cat=='choco')*"N-a6en17/c"
    url= "https://www.carrefour.es/supermercado/" + section
    sleep(1)
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    if soup.find('span', class_='plp-food-view__count')!= None:
        listed = soup.find('span', class_='plp-food-view__count').get_text()
        temp1 = listed.find('Mostrando') + 10
        temp2 = listed.find(' productos')
        pages = int((int(listed[temp1:temp2])+25)/25)
        print('listed ', listed,' products in ', pages,' pages')
        for n in range (1,pages+1):
            if n>1:
                url = url + "?No=" + str(24*(n-1))
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, 'html.parser')
            doc = soup.find_all('div', class_='product-card__parent')
            print(len(doc))
            for items in range (0,len(doc)):
                prod=doc[items]
                RAW_NAME = prod.find('h2', class_='product-card__title')
                RAW_CODE = RAW_NAME.find('a').get('href')
                RAW_PRICE = prod.find('span', class_='product-card__price')
                RAW_PRICE2 = prod.find('span', class_='product-card__price--current')
                RAW_PUM = prod.find('span', class_='product-card__price-per-unit')
                RAW_OLD = prod.find('span', class_='product-card__price--strikethrough')
                RAW_DEAL = prod.find('div', class_='product-card__badge')

                NAME = ' '.join(''.join(RAW_NAME.get_text()).split()) if RAW_NAME else None
                temp1 = int(RAW_CODE.find('/R-'))+3 if RAW_CODE else 0
                temp2 = len(RAW_CODE)-3 if RAW_CODE else 0
                CODE = RAW_CODE[temp1:temp2] if RAW_CODE else None
                PRICE = ' '.join(''.join(RAW_PRICE.get_text()).split()).strip() if RAW_PRICE else None
                PRICE2 = ' '.join(''.join(RAW_PRICE2.get_text()).split()).strip() if RAW_PRICE2 else None
                POLD = ' '.join(''.join(RAW_OLD.get_text()).split()).strip() if RAW_OLD else None
                PUM = ' '.join(''.join(RAW_PUM.get_text()).split()).strip() if RAW_PUM else None
                DEAL = ' '.join(''.join(RAW_DEAL.get_text()).split()).strip() if RAW_DEAL else None

                if page.status_code != 200:
                    raise ValueError('captha')

                data = {
                    'NAME': NAME,
                    'CODE': CODE,
                    'PRICE': PRICE,
                    'PRICE2': PRICE2,
                    'BRAND': '',
                    'PUM': PUM,
                    'POLD': POLD,
                    'CATEGORY': cat,
                    'SELLER': 'Carrefour',
                    'REVIEWS': '',
                    'STARS': '',
                    'SHIPPING': '',
                    'MANUFACTURER': '',
                    'VOLUME': '',
                    'RANK': '',
                    'DEAL': DEAL,
                }
                extracted_data.append(data)

def MercadonaParser(cat):
    firefox_profile = webdriver.FirefoxProfile()
    firefox_profile.set_preference('permissions.default.image', 2)
    firefox_profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')
    driver = webdriver.Firefox(firefox_profile=firefox_profile)
    login_url = 'https://tienda.mercadona.es/'
    driver.get(login_url)
    wait = WebDriverWait(driver, 3)
    sleep(3)
    pcodeElem = driver.find_element_by_name("postalCode")
    pcodeElem.send_keys("28020")        # Madrid 28036
    driver.find_element_by_css_selector('button.button-primary.button-big').click()
    sleep(3)
    section = (cat=='water')*156 + (cat=='sport')*163 + (cat=='cola')*158 + (cat=='fizzy')*159 + (cat=='tonic')*161 + (cat=='beer')*164 + \
              (cat=='teas')*162 + (cat=='milks')*72 + (cat=='juice1')*99 + (cat=='juice2')*100 + (cat=='juice3')*143 + (cat=='juice4')*98
    curl = 'https://tienda.mercadona.es/categories/' + str(section)
    driver.get(url= curl)
    wait.until(EC.visibility_of_element_located((By.ID, "root")))
    sleep(5)
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    sleep(2)
    doc = soup.find_all('div', class_='product-cell__info')
    print('Listed ' + str(len(doc)) + ' products')
    for items in range (0,len(doc)):
        prod=doc[items]
        RAW_NAME = prod.find('h4', class_='subhead1-r product-cell__description-name')
        RAW_SIZE = prod.find('div', class_='product-format')
        RAW_PRICE = prod.find('div', class_="product-price")

        NAME = ' '.join(''.join(RAW_NAME.get_text()).split()) if RAW_NAME else None
        VOLUME = ' '.join(''.join(RAW_SIZE.get_text()).split()).strip() if RAW_SIZE else None
        PRICE = ' '.join(''.join(RAW_PRICE.get_text()).split()).strip() if RAW_PRICE else None

        data = {
            'NAME': NAME,
            'CODE': '',
            'PRICE': PRICE,
            'PRICE2': '',
            'BRAND': '',
            'PUM': '',
            'POLD': '',
            'CATEGORY': cat,
            'SELLER': 'Mercadona',
            'REVIEWS': '',
            'STARS': '',
            'SHIPPING': '',
            'MANUFACTURER': '',
            'VOLUME': VOLUME,
            'RANK': '',
            'DEAL': '',
        }
        extracted_data.append(data)
    driver.quit()

def AlcampoParser(cat):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}
    section = (cat=='cola')*'WRefrescoCola' + (cat=='fizzy1')*'WRefrescoNaranja' + (cat=='fizzy2')*'WRefrescoLimon' + \
              (cat=='teas')*'W110308' + (cat=='tonic')*'W110303' + (cat=='sport')*'W110311' + (cat=='beer')*'W110701' + \
              (cat=='juice1')*'W110209' + (cat=='vegs')*'W6331072' + (cat=='juice2')*'W633107' + (cat=='juice3')*'W6331071' + \
              (cat=='juice4')*'W110210' + (cat=='water1')*'W1101041' + (cat=='water2')*'W1101042' + (cat=='water3')*'W1101043'
    url = "https://www.alcampo.es/compra-online/c/" + section
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    try:
        listed = soup.find('div', class_='totalResults').get_text()
    except AttributeError as e:
        return
    temp = listed.find(' ')
    pages = int((int(listed[0:temp]) + 49) / 49)
    print('listed ',listed[0:temp],' products in ', pages, ' pages')
    for n in range(1, pages + 1):
        if n > 1:
            m = str(n - 1)
            curl = url + "?page=" + m
            page = requests.get(curl, headers=headers)
            soup = BeautifulSoup(page.content, 'html.parser')
        doc = soup.find_all('div', class_='productGridItem')
        print(len(doc))
        for items in range (0,len(doc)):
            prod=doc[items]
            RAW_NAME = prod.find('div', class_='productName truncate')
            RAW_CODE = prod.find()
            RAW_PRICE = prod.find('div', class_="priceContainer")
            RAW_PUM = prod.find('span', class_='pesoVariable')
            RAW_BRAND = prod.find('div', class_='marca')

            NAME = ' '.join(''.join(RAW_NAME.get_text()).split()) if RAW_NAME else None
            CODE = RAW_CODE.a['id'] if RAW_CODE else None
            PRICE = ' '.join(''.join(RAW_PRICE.get_text()).split()).strip() if RAW_PRICE else None
            PUM = ' '.join(''.join(RAW_PUM.get_text()).split()).strip() if RAW_PUM else None
            BRAND = ' '.join(''.join(RAW_BRAND.get_text()).split()) if RAW_BRAND else None

            if page.status_code != 200:
                raise ValueError('captha')

            data = {
                'NAME': NAME,
                'CODE': CODE,
                'PRICE': PRICE,
                'PUM': PUM,
                'PRICE2': '',
                'POLD': '',
                'BRAND': BRAND,
                'CATEGORY': cat,
                'SELLER': 'Alcampo',
                'REVIEWS': '',
                'STARS': '',
                'SHIPPING': '',
                'MANUFACTURER': '',
                'VOLUME': '',
                'RANK': '',
                'DEAL': '',
            }
            extracted_data.append(data)

def SaveData(shop):
    with open('data.json', 'w') as outfile:
        json.dump(extracted_data, outfile, indent=4)
    cdate = time.strftime("%Y%m%d")
    df = pandas.read_json('data.json')
    fname = shop + '_%s.csv' % cdate
    df.to_csv(fname, encoding='utf-8-sig')
    sleep(1)
    os.remove('data.json')

if __name__ == "__main__":

    # Get current directory and clear data
    cwd = os.getcwd()
    
    # Scrape from Amazon
    extracted1 = []
    extracted2 = []

    amid = '262-0941104-5571657'  # with postcode 28020
    drinkcats = ['water', 'fizzy', 'teas', 'vegs', 'juice', 'choco', 'sports']
    random.shuffle(drinkcats)
    for i in drinkcats:
        sleep(3)
        itemlist = []
        AmazonCodes(i, amid)
        for z in itemlist[:59]:
            code = z
            AmazonParser(z, i, amid)

    # Dump data to CSV dataframe:
    with open('data.json', 'w') as outfile:
        json.dump(extracted1, outfile, indent=4)
    df1 = pandas.read_json('data.json')
    fname = 'amazon_temp1.csv'
    df1.to_csv(fname, encoding='utf-8-sig')
    os.remove('data.json')
    with open('data.json', 'w') as outfile:
        json.dump(extracted2, outfile, indent=4)
    df2 = pandas.read_json('data.json')
    fname = 'amazon_temp2.csv'
    df2.to_csv(fname, encoding='utf-8-sig')
    os.remove('data.json')
    # Combine both sets of information:
    cdate = time.strftime("%Y%m%d")
    full = pandas.merge(df1, df2, on='CODE', how='left')
    fname = 'amazon_%s.csv' % cdate
    full.to_csv(fname, encoding='utf-8-sig')
    
    # Scrape from Eroski
    extracted_data = []
    plist = ['water', 'fizzy', 'vegs', 'juice', 'beer']
    random.shuffle(plist)
    for i in plist:
        print("Processing: Eroski " + i)
        EroskiParser(i)
    SaveData('eroski')

    # Scrape from Carrefour
    extracted_data = []
    plist = ['water1', 'water2', 'water3', 'water4', 'juice1', 'juice2', 'beer', 'cola', 'fizzy', 'sport', 'tonic',
              'teas', 'energy', 'vegs', 'choco']
    random.shuffle(plist)
    for i in plist:
        print("Processing: Carrefour " + i)
        CarrefourParser(i)
    SaveData('carrefour')


    # Scrape from Alcampo
    extracted_data = []
    plist = ['cola', 'fizzy1', 'fizzy2', 'teas', 'tonic', 'sport', 'beer', 'juice1', 'vegs', 'juice2', 'juice3',
              'juice4', 'water1', 'water2', 'water3']
    random.shuffle(plist)
    for i in plist:
        print("Processing: Alcampo " + i)
        AlcampoParser(i)
    SaveData('alcampo')

    # Scrape from Mercadona
    extracted_data = []
    plist = ['water', 'sport', 'cola', 'fizzy', 'tonic', 'beer', 'teas', 'milks', 'juice1', 'juice2', 'juice3', 'juice4']
    random.shuffle(plist)
    for i in plist:
        print("Processing: Mercadona " + i)
        MercadonaParser(i)
    SaveData('mercadona')

