from numpy import inner
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
import datetime
import sys
def cleanhtml(raw_html):
    possible_text1 = "See the seller's listing for full details."
    possible_text2 = "See all condition definitions- opens in a new window or tab"
    possible_text3 = "... Read moreabout the condition"
    other_text = "Details about"
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    cleantext = cleantext.replace('\n','').replace('\t','').replace(possible_text1,"").replace(possible_text2,"").replace(possible_text3,"")
    cleantext = cleantext.replace(other_text,"").lstrip()
    return cleantext
class Ebay_Scraper():
    def __init__(self, starter_url, base_url):
        self.m=0
        self.curr_prod_link=""
        self.curr_prod_link_tag=""
        self.results=[]
        self.base_url = base_url
        self.headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0"}
        self.starter_url = starter_url
        self.start = time.time()
        r= requests.get(starter_url,  headers=self.headers)
        content = r.text
        soup = BeautifulSoup(content,'html.parser')
        products_count = soup.find("h2", attrs={"class":"srp-controls__count-heading"}).text.replace("Results","").replace(",","").replace(" ","")
        self.products_count = int(products_count)
        if soup.find("ul", attrs={"class":"srp-results"}):
            result = soup.find("ul", attrs={"class":"srp-results"})
        elif soup.find("ul", attrs={"class":"b-list__items_nofooter"}):
            result = soup.find("ul", attrs={"class":"b-list__items_nofooter"})
        else:
            result = soup.find("ul", attrs={"class":"b-list__items_nofooter srp-results srp-grid"})
        product_links = result.findAll("li", attrs={"class":"s-item"})
        products_count_per_page = len(product_links)
        self.pages_count = int(self.products_count/products_count_per_page)+1
        self.curr_page_num = 1
        self.curr_prod_num = 1
        self.curr_prod_in_page_num = 1

    def scrape_single_product(self, url):
        try:
            self.m+=1
            self.curr_prod_num=m
            self.curr_prod_link=url
            file_object = open('logs.txt', 'a')
            x = datetime.datetime.now()
            file_object.write('\n{} \t --- scraped URL ---- Product Page ---- {}'.format(x, url))
            file_object.close()
            while True:
                try:
                    inner_content= requests.get(url,  headers=self.headers).text
                    break
                except requests.exceptions.ConnectionError as e:
                    print("Time out Wait to re connect")
                    file_object = open('errors.txt', 'a')
                    x = datetime.datetime.now()
                    file_object.write('\n{} \t --- Unexpected error ---- {}'.format(x, e))
                    file_object.close()
                    end= time.time()
                    minutes = (end - self.start) / 60
                    print("Finished "+str(self.curr_page_num)+"/"+str(self.pages_count)+" pages. Finished "+str(self.curr_prod_num)+" / "+str(self.products_count)+" products in "+str(minutes)+" minutes")
                    time.sleep(5)
            inner_soup = BeautifulSoup(inner_content,'html.parser')
            f1 = open("example.html", "wb")
            f1.write(inner_content.encode("UTF-8"))
            f1.close()
            if inner_soup.find("div", attrs={"class":"item-details"}):
                while True:
                    try:
                        url = inner_soup.find("div", attrs={"class":"item-details"}).find("a").get("href")
                        curr_link=url
                        inner_content= requests.get(url,  headers=headers).text
                        inner_soup = BeautifulSoup(inner_content,'html.parser')
                        break
                    except requests.exceptions.ConnectionError:
                        print("Time out Wait to re connect")
                        file_object = open('errors.txt', 'a')
                        x = datetime.datetime.now()
                        file_object.write('\n{} \t --- Unexpected error ---- {}'.format(x, e))
                        file_object.close()
                        end= time.time()
                        minutes = (end - self.start) / 60
                        print("Finished "+str(i)+"/"+str(pages_num)+" pages. Finished "+str(j)+" / "+str(products_count)+" products in "+str(minutes)+" minutes")
                        time.sleep(5)
            if inner_soup.find("div" ,attrs={"id":"vi-itm-cond"}):
                item_condition = inner_soup.find("div" ,attrs={"id":"vi-itm-cond"}).text
            else:
                item_condition = inner_soup.find("div" ,attrs={"itemprop":"itemCondition"}).text
            item_title = cleanhtml(inner_soup.find("h1", attrs={"id":"itemTitle"}).text)
            Seller_desc=""
            if inner_soup.find("span", attrs={"class":"topItmCndDscMsg"}):
                Seller_desc = inner_soup.find("span", attrs={"class":"topItmCndDscMsg"}).text
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
                "price":price.replace("(including shipping)","").replace("US", "").lstrip() ,
                'item_title':item_title,
                'url':url
            }
            if inner_soup.find("div", attrs={"id":"viTabs_0_is"}):
                table_div = inner_soup.find("div", attrs={"id":"viTabs_0_is"})
                table = table_div.findAll("table")
                if len(table) > 1:
                    if Seller_desc == "":
                        if table[0].find("span", attrs={"id":"hiddenContent"}):
                            Seller_desc = table_div.find("span", attrs={"id":"hiddenContent"}).text
                            prod["seller_comment"]=Seller_desc
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
            else:
                specs_div = inner_soup.find("section", attrs={"class":"product-spectification"})
                specs_rows = specs_div.findAll("div", attrs={"class":"spec-row"})
                for spec_row in specs_rows:
                    ul = spec_row.find("ul")
                    lis = ul.findAll("li")
                    for li in lis:
                        name = li.find("div", attrs={"class":"s-name"}).text
                        value = li.find("div", attrs={"class":"s-value"}).text
                        prod[name] = value
            self.results.append(prod)
            end= time.time()
            minutes = (end - self.start) / 60
            self.curr_prod_num +=1
            if self.curr_prod_num%1000 == 0:
                pd.DataFrame(self.results).to_excel("NEW_Iphone_products_result3.xlsx")
            print("Finished "+str(self.curr_page_num)+"/"+str(self.pages_count)+" pages. Finished "+str(self.curr_prod_num)+" / "+str(self.products_count)+" products in "+str(minutes)+" minutes", end="\r")
        except Exception as e:
            file_object = open('errors.txt', 'a')
            x = datetime.datetime.now()
            file_object.write('\n{} \t --- Unexpected error ---- {}'.format(x, sys.exc_info()[0]))
            file_object.write('\n{} \t --- Unexpected error ---- {}'.format(x, e))
            file_object.write('\n{} \t --- Unexpected error ---- current page result {}'.format(x, self.curr_page_num))
            file_object.write('\n{} \t --- Unexpected error ---- current product number {}'.format(x, self.curr_prod_in_page_num))
            file_object.write('\n{} \t --- Unexpected error ---- URL tag where error happened {}'.format(x, self.curr_prod_link_tag))
            file_object.write('\n{} \t --- Unexpected error ---- URL where error happened {}'.format(x, self.curr_prod_link))
            file_object.close()
            end= time.time()
            minutes = (end - self.start) / 60
            print("Finished "+str(self.curr_page_num)+"/"+str(self.pages_count)+" pages. Finished "+str(self.curr_prod_num)+" / "+str(self.products_count)+" products in "+str(minutes)+" minutes")
            pd.DataFrame(results).to_excel("NEW_Iphone_products_result3.xlsx")
    
    
    def scrape_single_page_result(self,url):
        try:
            ebayUrl = self.base_url+str(i)
            while True:
                try:
                    r= requests.get(ebayUrl,  headers=self.headers)
                    break
                except requests.exceptions.ConnectionError as e:
                    print("Time out Wait to re connect")
                    file_object = open('errors.txt', 'a')
                    x = datetime.datetime.now()
                    file_object.write('\n{} \t --- Unexpected error ---- {}'.format(x, e))
                    file_object.close()
                    end= time.time()
                    minutes = (end - self.start) / 60
                    print("Finished "+str(self.curr_page_num)+"/"+str(self.pages_count)+" pages. Finished "+str(self.curr_prod_num)+" / "+str(self.products_count)+" products in "+str(minutes)+" minutes")
                    time.sleep(5)
            content = r.text
            soup = BeautifulSoup(content,'html.parser')
            if soup.find("ul", attrs={"class":"srp-results"}):
                result = soup.find("ul", attrs={"class":"srp-results"})
            elif soup.find("ul", attrs={"class":"b-list__items_nofooter"}):
                result = soup.find("ul", attrs={"class":"b-list__items_nofooter"})
            else:
                result = soup.find("ul", attrs={"class":"b-list__items_nofooter srp-results srp-grid"})
            if result:
                product_links = result.findAll("li", attrs={"class":"s-item"})
            else:
                f1 = open("example.html", "wb")
                f1.write(content.encode("UTF-8"))
                f1.close()
                pd.DataFrame(results).to_excel("NEW_Iphone_products_result3.xlsx")
                end= time.time()
                minutes = (end - self.start) / 60
                print("Finished "+str(self.curr_page_num)+"/"+str(self.pages_count)+" pages. Finished "+str(self.curr_prod_num)+" / "+str(self.products_count)+" products in "+str(minutes)+" minutes")
                sys.exit()
            self.curr_prod_in_page_num=1
            file_object = open('logs.txt', 'a')
            x = datetime.datetime.now()
            file_object.write('\n{} \t --- scraped URL ---- Main Page ---- {}'.format(x, ebayUrl))
            file_object.close()
            for prod_link in product_links:
                self.curr_prod_link_tag = prod_link
                url= prod_link.find("a", attrs={"class":"s-item__link"}).get("href")
                self.scrape_single_product(url)
                self.curr_prod_in_page_num+=1
                self.curr_prod_num+=1
        except Exception as e:
            file_object = open('errors.txt', 'a')
            x = datetime.datetime.now()
            file_object.write('\n{} \t --- Unexpected error ---- {}'.format(x, sys.exc_info()[0]))
            file_object.write('\n{} \t --- Unexpected error ---- {}'.format(x, e))
            file_object.write('\n{} \t --- Unexpected error ---- current page result {}'.format(x, self.curr_page_num))
            file_object.write('\n{} \t --- Unexpected error ---- current product number {}'.format(x, self.curr_prod_in_page_num))
            file_object.write('\n{} \t --- Unexpected error ---- URL tag where error happened {}'.format(x, self.curr_prod_link_tag))
            file_object.write('\n{} \t --- Unexpected error ---- URL where error happened {}'.format(x, self.curr_prod_link))
            file_object.close()
            end= time.time()
            minutes = (end - self.start) / 60
            print("Finished "+str(self.curr_page_num)+"/"+str(self.pages_count)+" pages. Finished "+str(self.curr_prod_num)+" / "+str(self.products_count)+" products in "+str(minutes)+" minutes")
            pd.DataFrame(self.results).to_excel("NEW_Iphone_products_result3.xlsx")

    def scrape_ebay_category(self):
        for i in range(1,self.pages_count):
            self.curr_page_num=i
            url = self.base_url+str(i)
            self.scrape_single_page_result(url)
            self.save()
    
    def save(self):
        pd.DataFrame(self.results).to_excel("Final_NEW_Iphone_products_results.xlsx")
            



scraper = Ebay_Scraper("https://www.ebay.com/b/Apple-Cell-Phones-Smartphones/9355/bn_319682?_pgn=1",
"https://www.ebay.com/b/Apple-Cell-Phones-Smartphones/9355/bn_319682?_pgn=")
Ebay_Scraper.scrape_ebay_category()

    




