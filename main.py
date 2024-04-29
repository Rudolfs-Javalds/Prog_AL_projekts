import requests, PySimpleGUI as sg, json
from bs4 import BeautifulSoup
import ast
import sqlite3


kas_janomaina = ['ā', 'č', 'ē', 'ģ', 'ī', 'ķ', 'ļ', 'ņ', 'š', 'ū', 'ž', ' ', '.', ',', '+']
uz_ko_janomaina = ['a', 'c', 'e', 'g', 'i', 'k', 'l', 'n', 's', 'u', 'z', '-', '', '', '']
kategorijas_rimi = {"Augļi":"SH-2-1", "Ogas":"SH-2-1", "Dārzeņi":"SH-2-2"}
kategorijas_maxima = {"Augļi":"Augļi un dārzeņi/Augļi un ogas", "Ogas":"Augļi un dārzeņi/Augļi un ogas", "Dārzeņi":"Augļi un dārzeņi/Dārzeņi"}
kategorijas = ["Augļi", "Ogas", "Dārzeņi"]
valutas = ["EUR", "USD", "GBP", "SEK", "PLN", "NOK", "JPY"]
valutas_meklesana ={"EUR":"eur", "USD":"tusd", "GBP": "gbp", "SEK":"sek", "PLN":"pln", "NOK":"nok", "JPY":"jpy"}
valutas_ziimes = {"EUR":'€', "USD":'$',  "GBP":'£', "SEK":'SEK', "PLN":'zł', "NOK":'NOK', "JPY":'¥'}
valutas_maina = requests.get("https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/eur.json").json()
lst = sg.Combo(kategorijas, enable_events=True, key='-COMBO-', readonly=True)
last_val = sg.Combo(valutas, enable_events=True, key='-COMBO_VALUTA-', readonly=True)

layout = [ [sg.Text("Lūdzu, ievadiet kādu preci meklējat: "), sg.Input(key='-INPUT-', enable_events=True)],
           [sg.Text("Izvēlieties šīs preces kategoriju: "), lst, sg.Text("Izvēlēties kādā valūtā rādīt cenas: "), last_val],# sg.Combo(kategorijas, key='-COMBO-', enable_events=True, readonly=True)]
           [sg.Button("Meklēt")],
           [sg.Text("Lētākā prece Rimi veikalā: "), sg.Text("", key='-OUTPUT_RIMI-')],
           [sg.Text("Lētākā prece Maxima veikalā: "), sg.Text("", key='-OUTPUT_MAXIMA-')],
           [sg.Text("Hipersaite uz preci Rimi veikalā: "), sg.InputText("", key='-SAITE_RIMI-', enable_events=True, font=("Arial", 11, "underline"), readonly=True)],
           [sg.Text("Hipersaite uz preci Maxima veikalā: "), sg.InputText("", key='-SAITE_MAXIMA-', enable_events=True, font=("Arial", 11, "underline"), readonly=True)]]

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
    saite = 'https://www.rimi.lv/e-veikals/lv/produkti/augli-un-darzeni/darzeni/c/'+ str(rez_1['category']) + '/' + nosaukums + '/p/' + str(rez_1['id'])
    print(saite)
    lapa_2 = requests.get(saite)
    zupa_2 = BeautifulSoup(lapa_2.content, "html.parser")
    rez_2 = str(zupa_2.find("p", {"class":"price-per"}))
    rez_sarakste = rez_2.split('\n')
    # print(rez_sarakste)
    try:
        # kursors.execute(f"INSERT INTO preces (ID_prece, veikals, prece, cena, mervieniba) VALUES ('{k}', 'rimi', '{ko_mekle}', '{float(rez_sarakste[1].strip().replace(',', '.'))}', '{rez_sarakste[2].strip().split('/')[1]}');")
        # print(k)
        # k=+1
        print(float(rez_sarakste[1].strip().replace(',', '.')), rez_sarakste[2].strip().split('/')[1], saite)
        return float(rez_sarakste[1].strip().replace(',', '.')), rez_sarakste[2].strip().split('/')[1], saite
    except:
        # print(float(rez_sarakste[1].strip().replace(',', '.')), rez_sarakste[2].strip().split('/')[1], saite)
        return 0, 'nepastāv', 'nepastāv'
    

def maxima_cena(ko_mekle, kategorija):
    URL = f"https://www.barbora.lv/meklet?order=priceAsc&q={str(ko_mekle).lower()}"
    # print(URL)
    lapa_1 = requests.get(URL)
    zupa_1 = BeautifulSoup(lapa_1.content, "html.parser")
    cik=0

    for n in zupa_1.find_all('script'):
        cik+=1
        if cik==21: # 22. pēc kārtas ir tieši tas info, ko man vajag / pēc kā var turpināt meklēt
            n = str(n).replace('window.b_productList = ', '').replace("<script>", '').replace("</script>", '').replace("false", '"false"').replace("true", '"true"').replace("null", '"null"').replace("{[", '{').replace("]}", '}').replace("[}", "[]}").strip()
            n=n.replace(',', ',\n')
            with open('dati_maxima.txt', 'w', encoding='utf-8') as txt_f:
                txt_f.write(n)
            with open('dati_maxima.txt', 'r+', encoding='utf-8') as txt_f:
                linijas = txt_f.readlines()
                with open('dati_maxima.json', 'w', encoding='utf-8') as json_f:
                    for k in range(len(linijas)):
                        # print (k, linijas)
                        # print (k, len(linijas))
                        if k!=0 and (linijas[k][0]!='[' and linijas[k][0]!='{' and linijas[k][0]!='"'):
                            linijas[k-1]=linijas[k-1].replace('\n', '')
                            # print(linijas[k])
                        if k!=0:
                            json_f.write(linijas[k-1])
                with open('dati_maxima.json', 'a', encoding='utf-8') as json_f:
                    json_f.write(linijas[-1].replace(';', ''))
                    
            f = open('dati_maxima.json', 'r', encoding="utf-8")
            data = json.load(f)
            f.close()
            # print(type(data))
            for produkts in data:
                if kategorija.lower() in produkts["category_name_full_path"].lower() and "tvaicēti" not in produkts["category_name_full_path"].lower() and "saldēti" not in produkts["category_name_full_path"].lower() and "apstrādāti" not in produkts["category_name_full_path"].lower():
                    # print(produkts['units'][0]['price'])
                    # print(produkts)
                    cena_maxima = float(produkts['units'][0]['price'])
                    mervien_maxima = produkts['units'][0]['unit']
                    nosaukums_maxima = str(produkts['title']).lower()
                    for i in range(0, len(kas_janomaina)):
                        nosaukums_maxima = nosaukums_maxima.replace(kas_janomaina[i], uz_ko_janomaina[i])
                    for i in range(1, len(nosaukums_maxima)):
                        if(nosaukums_maxima[i-1].isnumeric() and nosaukums_maxima[i].isalpha()):
                            nosaukums_maxima = f'{nosaukums_maxima[:i]}-{nosaukums_maxima[i:]}'
                    saite_maxima = (f"https://www.barbora.lv/produkti/{nosaukums_maxima}")
                    print(cena_maxima, mervien_maxima, saite_maxima)
                    # kursors.execute(f"INSERT INTO preces (ID_prece, veikals, prece, cena, mervieniba) VALUES ({k}, 'maxima', '{ko_mekle}', '{cena_maxima}', '{mervien_maxima}');")
                    # print(k)
                    # k=+1
                    return cena_maxima, mervien_maxima, saite_maxima

            


# maxima_cena("burk%25C4%2581ni", "Augļi un dārzeņi/Dārzeņi")
def main():
    savienojums = sqlite3.connect("dati.db")
    kursors=savienojums.cursor()
    kursors.execute("CREATE TABLE IF NOT EXISTS maxima(ID_maxima INTEGER PRIMARY KEY UNIQUE, prece TEXT, cena REAL, mervieniba TEXT, hipersaite TEXT)")
    kursors.execute("CREATE TABLE IF NOT EXISTS rimi(ID_rimi INTEGER PRIMARY KEY UNIQUE, prece TEXT, cena REAL, mervieniba TEXT, hipersaite TEXT)")
    kursors.execute("SELECT max(ID_maxima) FROM maxima")
    ID_maxima = kursors.fetchone()[0]
    kursors.execute("SELECT max(ID_rimi) FROM rimi")
    ID_rimi = kursors.fetchone()[0]
    if (ID_maxima == None):
        ID_maxima = 1
    else:
        ID_maxima+=1
    if (ID_rimi == None):
        ID_rimi = 1
    else:
        ID_rimi+=1
    kursors.close()
    window = sg.Window('Projekts', layout)
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
        if event == 'Meklēt':
            kursors = savienojums.cursor()
            
            kategorijas_rimi_id=kategorijas_rimi[values['-COMBO-']]
            kategorijas_maxima_id=kategorijas_maxima[values['-COMBO-']]
            # print(values['-COMBO_VALUTA-'], valutas_meklesana[values['-COMBO_VALUTA-']], valutas_maina['eur']['eur'])
            # valutas_kurss = 1
            valutas_kurss = float(valutas_maina['eur'][valutas_meklesana[values['-COMBO_VALUTA-']]])
            valutas_zime = valutas_ziimes[values['-COMBO_VALUTA-']]
            if kursors.execute("SELECT cena FROM rimi WHERE prece = ?", [str(values['-INPUT-']).lower()]).fetchone() == None:
                cena_rimi, mervien_rimi, hipersaite_rimi = rimi_cena(values['-INPUT-'], kategorijas_rimi_id)
                kursors.execute("INSERT INTO rimi(ID_rimi, prece, cena, mervieniba, hipersaite) VALUES (?, ?, ?, ?, ?)", (ID_rimi, str(values['-INPUT-']).lower(), cena_rimi, mervien_rimi, hipersaite_rimi))
                ID_rimi+=1
            else:
                # print((values['-INPUT-']))
                kursors.execute("SELECT cena, mervieniba, hipersaite FROM rimi WHERE prece = ?", [str(values['-INPUT-']).lower()])
                cena_rimi, mervien_rimi, hipersaite_rimi = kursors.fetchone()

            if kursors.execute("SELECT cena FROM maxima WHERE prece = ?", [str(values['-INPUT-']).lower()]).fetchone() == None:
                # print("nav maximā")
                cena_maxima, mervien_maxima, hipersaite_maxima = maxima_cena(values['-INPUT-'], kategorijas_maxima_id)
                kursors.execute("INSERT INTO maxima(ID_maxima, prece, cena, mervieniba, hipersaite) VALUES (?, ?, ?, ?, ?)", (ID_maxima, str(values['-INPUT-']).lower(), cena_maxima, mervien_maxima, hipersaite_maxima))
                ID_maxima+=1
            else:
                kursors.execute("SELECT cena, mervieniba, hipersaite FROM maxima WHERE prece = ?", [str(values['-INPUT-']).lower()])
                cena_maxima, mervien_maxima, hipersaite_maxima = kursors.fetchone()
            # print(cena_rimi, mervien_rimi, hipersaite_rimi)
            # print(cena_maxima, mervien_maxima, hipersaite_maxima)
            # print(ID_maxima, ID_rimi)
            savienojums.commit()
            kursors.close()
            window['-OUTPUT_RIMI-'].update(value = f'{cena_rimi*valutas_kurss:.2f} {valutas_zime}/{mervien_rimi}')
            window['-SAITE_RIMI-'].update(value = hipersaite_rimi)
            window['-OUTPUT_MAXIMA-'].update(value = f'{cena_maxima*valutas_kurss:.2f} {valutas_zime}/{mervien_maxima}')
            window['-SAITE_MAXIMA-'].update(value = hipersaite_maxima)
            if cena_rimi == 0:
                window['-OUTPUT_RIMI-'].update(value="Diemžēl šāds produkts nav pieejams")
                window['-SAITE_RIMI-'].update(value = "")

    window.close()


if __name__ == "__main__":
    main()