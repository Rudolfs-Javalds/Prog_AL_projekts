import requests, PySimpleGUI
from bs4 import BeautifulSoup

def rimi_cena(ko_mekle, kategorija): # Dārzeņi = "SH-2-2"
    URL = "https://www.rimi.lv/e-veikals/lv/meklesana?currentPage=1&pageSize=20&query=" + ko_mekle + "%3Apriceunit-asc%3AassortmentStatus%3AinAssortment%3AallCategories%3A" + kategorija
    lapa_1 = requests.get(URL)
    zupa_1 = BeautifulSoup(lapa_1.content, "html.parser")
    id = str(zupa_1.find("a", {"class":"card__url js-gtm-eec-product-click"},).get("href"))
    lapa_2 = requests.get(f'https://www.rimi.lv{id}')
    zupa_2 = BeautifulSoup(lapa_2.content, "html.parser")
    rez = str(zupa_2.find("p", {"class":"price-per"}))
    rez_sarakste = rez.split('\n')
    return float(rez_sarakste[1].strip().replace(',', '.'))

print(f'{rimi_cena("tomāti", "SH-2-2")} EUR/kg')
