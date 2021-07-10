import requests
from bs4 import BeautifulSoup
for i in range(1,10):
    headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0"}
    ebayUrl = "https://www.ebay.com/sch/i.html?_from=R40&_nkw=iphone&_sacat=0&_pgn="+str(i)
    r= requests.get(ebayUrl,  headers=headers)
    content = r.text
    soup = BeautifulSoup(content,'html.parser')
    product_links = soup.findAll("a", attrs={"class":"s-item__link"})
    f1 = open("ebay_results/page_"+str(i)+".html", "wb")
    f1.write(content.encode("UTF-8"))
    f1.close()
    print("Finished "+str(i), end="\r")