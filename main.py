import requests, PySimpleGUI as sg, json
from bs4 import BeautifulSoup

kas_janomaina = ['ā', 'č', 'ē', 'ģ', 'ī', 'ķ', 'ļ', 'ņ', 'š', 'ū', 'ž', ' ', '.', ',']
uz_ko_janomaina = ['a', 'c', 'e', 'g', 'i', 'k', 'l', 'n', 's', 'u', 'z', '-', '', '']
kategorijas_rimi = {"Augļi":"SH-2-1", "Ogas":"SH-2-1", "Dārzeņi":"SH-2-2"}
kategorijas = ["Augļi", "Ogas", "Dārzeņi"]
lst = sg.Combo(kategorijas, enable_events=True, key='-COMBO-', readonly=True)

layout = [ [sg.Text("Lūdzu, ievadiet kādu preci meklējat: "), sg.Input(key='-INPUT-', enable_events=True)],
           [sg.Text("Iezvēlieties šīs preces kategoriju: "), lst],# sg.Combo(kategorijas, key='-COMBO-', enable_events=True, readonly=True)]
           [sg.Button("Meklēt")],
           [sg.Text("Lētāka prece Rimi veikalā: "), sg.Text("", key='-OUTPUT-')]]

def rimi_cena(ko_mekle, kategorija):
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
    nosaukums  = str(rez_1['name']).lower() 
    for i in range(0, len(kas_janomaina)):
        nosaukums = nosaukums.replace(kas_janomaina[i], uz_ko_janomaina[i])
    saite = 'https://www.rimi.lv/e-veikals/lv/produkti/augli-un-darzeni/darzeni/'+ str(rez_1['category']) + '/' + nosaukums + '/p/' + str(rez_1['id'])
    # print(saite)
    lapa_2 = requests.get(saite)
    zupa_2 = BeautifulSoup(lapa_2.content, "html.parser")
    rez_2 = str(zupa_2.find("p", {"class":"price-per"}))
    rez_sarakste = rez_2.split('\n')
    try:
        return float(rez_sarakste[1].strip().replace(',', '.'))
    except:
        return 0

window = sg.Window('Projekts', layout)
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break
    if event == 'Meklēt':
        kategorijas_id=kategorijas_rimi[values['-COMBO-']]
        cena_rimi = rimi_cena(values['-INPUT-'], kategorijas_id)
        if cena_rimi == 0:
            window['-OUTPUT-'].update(value="Diemžēl šāds produkts nav pieejams")
        else:
            window['-OUTPUT-'].update(value=f'{cena_rimi} EUR/kg')
window.close()
# print(f'{rimi_cena("tomāti", "SH-2-2")} EUR/kg')
