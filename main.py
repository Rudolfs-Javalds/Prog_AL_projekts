import requests, PySimpleGUI, json
from bs4 import BeautifulSoup

ipasie_burti = ['ā', 'č', 'ē', 'ģ', 'ī', 'ķ', 'ļ', 'ņ', 'š', 'ū', 'ž']
parastie_burti = ['a', 'c', 'e', 'g', 'i', 'k', 'l', 'n', 's', 'u', 'z']

def rimi_cena(ko_mekle, kategorija): # Dārzeņi = "SH-2-2"
    URL = "https://www.rimi.lv/e-veikals/lv/meklesana?currentPage=1&pageSize=20&query=" + ko_mekle + "%3Apriceunit-asc%3AassortmentStatus%3AinAssortment%3AallCategories%3A" + kategorija
    lapa_1 = requests.get(URL)
    zupa_1 = BeautifulSoup(lapa_1.content, "html.parser")
    rez_1 = json.loads(str(zupa_1.find("div", {"class":"js-product-container card -horizontal-for-mobile"}).get("data-gtm-eec-product"))) #Atrod produkta info
    while str(ko_mekle).lower() not in str(rez_1['name']).lower(): # Ja tā nosaukumā nav ko meklē
        rez = zupa_1.find_all("div", {"class":"js-product-container card -horizontal-for-mobile"}) # Atrast visus 'div', kuri ir priekš produktiem
        for i in rez: # Iziet cauri katram šim 'div'
            if str(ko_mekle).lower() in str(json.loads(str(i.get('data-gtm-eec-product')))['name']).lower(): # Ja 'div' iekšā ir meklējamā nosaukums
                rez_1=json.loads(str(i.get('data-gtm-eec-product'))) # rez_1 ir info par šo produktu
                break
        break
    nosaukums  = str(rez_1['name']).lower().replace(' ', '-').replace('.', '')
    for i in range(0, 11):
        nosaukums = nosaukums.replace(ipasie_burti[i], parastie_burti[i])
    saite = 'https://www.rimi.lv/e-veikals/lv/produkti/augli-un-darzeni/darzeni/'+ str(rez_1['category']) + '/' + nosaukums + '/p/' + str(rez_1['id'])
    print(saite)
    lapa_2 = requests.get(saite)
    zupa_2 = BeautifulSoup(lapa_2.content, "html.parser")
    rez_2 = str(zupa_2.find("p", {"class":"price-per"}))
    rez_sarakste = rez_2.split('\n')
    return float(rez_sarakste[1].strip().replace(',', '.'))

print(f'{rimi_cena("tomāti", "SH-2-2")} EUR/kg')
