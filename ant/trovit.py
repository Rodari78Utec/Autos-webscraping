from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
import time

# Configuración del navegador
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # Ejecutar en modo headless (sin abrir una ventana del navegador)
options.binary_location = '/usr/bin/chromium-browser'  # Ubicación del binario de Chromium

# Path del chromedriver
chromedriver_path = '/usr/lib/chromium-browser/chromedriver'  # Ubicación del chromedriver


# Función para extraer datos de una página
def get_html_from_page(url):
    # Iniciar el navegador
    driver = webdriver.Chrome(service=Service(chromedriver_path), options=options)
    driver.get(url)

    # Esperar un tiempo para que la página se cargue completamente
    time.sleep(5)

    # Obtener el contenido HTML de la página
    html = driver.page_source

    # Cerrar el navegador
    driver.quit()

    # Analizar el contenido HTML con BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')

    return soup
# Iniciar el navegador

def extrac_gastype_transmision(url):
    
    soup = get_html_from_page(url)

    

    return False

url = 'https://autos.trovit.com.pe/autos-usados/peru'

soup = get_html_from_page(url)

# driver = webdriver.Chrome(service=Service(chromedriver_path), options=options)

# # URL de la página de NeoAuto con vehículos usados
# url = 'https://autos.trovit.com.pe/autos-usados/peru'
# driver.get(url)

# # Esperar un tiempo para que la página se cargue completamente
# time.sleep(5)

# # Obtener el contenido HTML de la página
# html = driver.page_source

# # Imprimir el HTML para verificar que se cargó correctamente
# #with open("outputtrovit.html", "w", encoding='utf-8') as file:
# #    file.write(html)

# # Cerrar el navegador
# driver.quit()

# # Analizar el contenido HTML con BeautifulSoup
# soup = BeautifulSoup(html, 'html.parser')

# Listado de contenedores de vehículos
listings = soup.find_all('div', class_='item js-item js-backToTrovit item-cars-snippet')

# Imprimir el número de listados encontrados
print(f"Number of listings found: {len(listings)}")

# Variables para almacenar datos
titles = []
carsubtitles =[]
prices = []
links = []
years = []
mileages = []
gastype =[]
transmision =[]
locations = []

# Extraer datos de cada contenedor
for listing in listings:
    title = listing.find('h4', class_='item-title').text.strip() if listing.find('h4', class_='item-title') else 'N/A'
    carsubtitle = ""
    price = listing.find('div', class_='item-price-container').text.strip() if listing.find('div', class_='item-price-container') else 'N/A'
    link = 'http:' + listing.find('img', class_='snippet-image')['src'] if listing.find('img', class_='snippet-image') else 'N/A'

   
    
    location = listing.find('h5', class_='item-address').text.strip() if listing.find('h5', 'item-address') else 'N/A'

    detaillistings = listing.find_all('div', class_='item-property')
    #print(f"Number of detail listings found: {len(detaillistings)}")
    year = ""
    mileage = ""
    for detail in detaillistings:
        if year=="":
            year = detail.text.strip() 
        else :
            mileage = detail.text.strip()         


    titles.append(title)
    carsubtitles.append(carsubtitle)
    prices.append(price)
    links.append(link)
    years.append(year)
    #gastype.append(gastypetransmision[0])
    #transmision.append(gastypetransmision[1])
    mileages.append(mileage)
    locations.append(location)

# Crear un DataFrame con los datos extraídos
data = {
    'Title': titles,
    'Subtitle': carsubtitles,
    'Price': prices,
    'Link': links,
    'Year': years,
    'km': mileages,
    'Location': locations
}

df = pd.DataFrame(data)

# Guardar los datos en un archivo CSV
df.to_csv('neoauto_vehiclestrovit.csv', index=False)

print("Datos extraídos y guardados en neoauto_vehicles.csv")
