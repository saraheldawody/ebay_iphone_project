import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
import datetime
def cleanhtml(raw_html):
    possible_text1 = "See the seller's listing for full details."
    possible_text2 = "See all condition definitions- opens in a new window or tab"
    possible_text3 = "... Read moreabout the condition"
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    cleantext = cleantext.replace('\n','').replace('\t','').replace(possible_text1,"").replace(possible_text2,"").replace(possible_text3,"")
    return cleantext
start = time.time()
results = []
for i in range(1,10):
    headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0"}
    ebayUrl = "https://www.ebay.com/sch/i.html?_from=R40&_nkw=iphone&_sacat=0&_pgn="+str(i)
    r= requests.get(ebayUrl,  headers=headers)
    content = r.text
    soup = BeautifulSoup(content,'html.parser')
    result = soup.find("ul", attrs={"class":"srp-results"})
    product_links = result.findAll("li", attrs={"class":"s-item"})
    prod_count = len(product_links)
    time.sleep(1)
    j=0
    for prod_link in product_links:
        j+=1
        url= prod_link.find("a", attrs={"class":"s-item__link"}).get("href")
        file_object = open('logs.txt', 'a')
        x = datetime.datetime.now()
        file_object.write('{} \t --- scraped URL ---- {}'.format(x, url))
        file_object.close()
        while True:
            try:
                inner_content= requests.get(url,  headers=headers).text
                break
            except requests.exceptions.ConnectionError:
                print("Time out Wait to re connect")
                time.sleep(5)
        inner_soup = BeautifulSoup(inner_content,'html.parser')
        f1 = open("example.html", "wb")
        f1.write(inner_content.encode("UTF-8"))
        f1.close()
        table_div = inner_soup.find("div", attrs={"id":"viTabs_0_is"})
        table = table_div.findAll("table")
        item_condition = inner_soup.find("div" ,attrs={"id":"vi-itm-cond"}).text
        Seller_desc=""
        if inner_soup.find("span", attrs={"class":"topItmCndDscMsg"}):
            Seller_desc = inner_soup.find("span", attrs={"class":"topItmCndDscMsg"}).text
        if len(table) > 1:
            if Seller_desc == "":
                if table[0].find("span", attrs={"id":"hiddenContent"}):
                    Seller_desc = table_div.find("span", attrs={"id":"hiddenContent"}).text
        price=""
        if inner_soup.find("span", attrs={"id":"convbidPrice"}):
            price=inner_soup.find("span", attrs={"id":"convbidPrice"}).text
        if price == "":
            if inner_soup.find("span", attrs={"id":"convbinPrice"}):
                price=inner_soup.find("span", attrs={"id":"convbinPrice"}).text
        if price == "":
            if inner_soup.find("span", attrs={"id":"prcIsum"}):
                price = inner_soup.find("span", attrs={"id":"prcIsum"}).text
            elif inner_soup.find("span",attrs={"id":"prcIsum_bidPrice"}) :
                price = inner_soup.find("span",attrs={"id":"prcIsum_bidPrice"}).text
            elif inner_soup.find("span",attrs={"id":"mm-saleDscPrc"}):
                price = inner_soup.find("span",attrs={"id":"mm-saleDscPrc"}).text
            else:
                price = inner_soup.find("span", attrs={"class":"vi-VR-cvipPrice"}).text
        prod = {
            "condition":item_condition,
            "seller_comment":Seller_desc,
            "price":price.replace("(including shipping)",""),
            'url':url
        }
        if len(table) > 1:
            k=1
        else:
            k=0
        for tr in table[k].findAll("tr"):
            tds = tr.findAll("td")
            if len(tds) == 0:
                continue
            if len(tds) > 2:
                first_label = cleanhtml(tds[0].text)
                first_value = cleanhtml(tds[1].text)
                second_label = cleanhtml(tds[2].text)
                second_value = cleanhtml(tds[3].text)
                prod[first_label]=first_value
                prod[second_label]=second_value
            else:
                first_label = cleanhtml(tds[0].text)
                first_value = cleanhtml(tds[1].text)
                prod[first_label]=first_value
        results.append(prod)
        pd.DataFrame(results).to_excel("Iphone_products_result.xlsx")
        end= time.time()
        minutes = (end - start) / 60
        print("Finished "+str(i)+"/10 pages. Finished "+str(j)+" / "+str(prod_count)+" products in "+str(minutes)+" minutes", end="\r")