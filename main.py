import requests, PySimpleGUI as sg, json
from bs4 import BeautifulSoup

kas_janomaina = ['ā', 'č', 'ē', 'ģ', 'ī', 'ķ', 'ļ', 'ņ', 'š', 'ū', 'ž', ' ', '.', ',', '+']
uz_ko_janomaina = ['a', 'c', 'e', 'g', 'i', 'k', 'l', 'n', 's', 'u', 'z', '-', '', '', '']
kategorijas_rimi = {"Augļi":"SH-2-1", "Ogas":"SH-2-1", "Dārzeņi":"SH-2-2"}
kategorijas = ["Augļi", "Ogas", "Dārzeņi"]
lst = sg.Combo(kategorijas, enable_events=True, key='-COMBO-', readonly=True)

layout = [ [sg.Text("Lūdzu, ievadiet kādu preci meklējat: "), sg.Input(key='-INPUT-', enable_events=True)],
           [sg.Text("Iezvēlieties šīs preces kategoriju: "), lst],# sg.Combo(kategorijas, key='-COMBO-', enable_events=True, readonly=True)]
           [sg.Button("Meklēt")],
           [sg.Text("Lētāka prece Rimi veikalā: "), sg.Text("", key='-OUTPUT_RIMI-')],
           [sg.Text("Hipersaite uz preci Rimi veikalā: "), sg.InputText("", key='-SAITE_RIMI-', enable_events=True, font=("Arial", 11, "underline"), readonly=True)]]

def rimi_cena(ko_mekle, kategorija):
    URL = "https://www.rimi.lv/e-veikals/lv/meklesana?currentPage=1&pageSize=20&query=" + ko_mekle + "%3Apriceunit-asc%3AassortmentStatus%3AinAssortment%3AallCategories%3A" + kategorija
    lapa_1 = requests.get(URL)
    zupa_1 = BeautifulSoup(lapa_1.content, "html.parser")
    # print(zupa_1.prettify())
    rez_1 = json.loads(str(zupa_1.find("div", {"class":"js-product-container card -horizontal-for-mobile"}).get("data-gtm-eec-product"))) #Atrod produkta info
    # print(str(ko_mekle).lower(), str(rez_1['name']).lower(), (str(ko_mekle).lower() in str(rez_1['name']).lower()))
    while str(ko_mekle).lower() not in str(rez_1['name']).lower(): # Ja tā nosaukumā nav ko meklē
        rez = zupa_1.find_all("div", {"class":"js-product-container card -horizontal-for-mobile"}) # Atrast visus 'div', kuri ir priekš produktiem
        for i in rez: # Iziet cauri katram šim 'div'
            if str(ko_mekle).lower() in str(json.loads(str(i.get('data-gtm-eec-product')))['name']).lower(): # Ja 'div' iekšā ir meklējamā nosaukums
                # print(str(ko_mekle))
                rez_1=json.loads(str(i.get('data-gtm-eec-product'))) # rez_1 ir info par šo produktu
                break
        break
    nosaukums  = str(rez_1['name']).lower() 
    for i in range(0, len(kas_janomaina)):
        nosaukums = nosaukums.replace(kas_janomaina[i], uz_ko_janomaina[i])
    saite = 'https://www.rimi.lv/e-veikals/lv/produkti/augli-un-darzeni/darzeni/'+ str(rez_1['category']) + '/' + nosaukums + '/p/' + str(rez_1['id'])
    # print(saite)
    lapa_2 = requests.get(saite)
    zupa_2 = BeautifulSoup(lapa_2.content, "html.parser")
    rez_2 = str(zupa_2.find("p", {"class":"price-per"}))
    rez_sarakste = rez_2.split('\n')
    # print(rez_sarakste)
    try:
        return float(rez_sarakste[1].strip().replace(',', '.')), rez_sarakste[2].strip(), saite
    except:
        return 0, ""
    

def maxima_cena(ko_mekle, kategorija):
    URL = f"https://www.barbora.lv/meklet?order=priceAsc&q={str(ko_mekle).lower()}"
    lapa_1 = requests.get(URL)
    zupa_1 = BeautifulSoup(lapa_1.content, "html.parser")
    # print(zupa_1)
    cik=0
    for n in zupa_1.find_all('script'):
        cik+=1
        if cik==21: # 22. pēc kārtas ir tieši tas info, ko man vajag / pēc kā var turpināt meklēt
            print(n)


maxima_cena("burk%25C4%2581ni", "dārzeņi")
window = sg.Window('Projekts', layout)
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break
    if event == 'Meklēt':
        kategorijas_id=kategorijas_rimi[values['-COMBO-']]
        cena_rimi, mervien_rimi, hipersaite_rimi = rimi_cena(values['-INPUT-'], kategorijas_id)
        if cena_rimi == 0:
            window['-OUTPUT_RIMI-'].update(value="Diemžēl šāds produkts nav pieejams")
        else:
            window['-OUTPUT_RIMI-'].update(value = f'{cena_rimi} {mervien_rimi}')
            window['-SAITE_RIMI-'].update(value = hipersaite_rimi)
window.close()
# print(f'{rimi_cena("tomāti", "SH-2-2")} EUR/kg')
