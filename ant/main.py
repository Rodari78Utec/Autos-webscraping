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

# Iniciar el navegador
driver = webdriver.Chrome(service=Service(chromedriver_path), options=options)

# URL de la página de NeoAuto con vehículos usados
url = 'https://neoauto.com/venta-de-autos-usados?page=285'
driver.get(url)

# Esperar un tiempo para que la página se cargue completamente
time.sleep(5)

# Obtener el contenido HTML de la página
html = driver.page_source

# Imprimir el HTML para verificar que se cargó correctamente
#with open("output.html", "w", encoding='utf-8') as file:
#    file.write(html)

# Cerrar el navegador
driver.quit()

# Analizar el contenido HTML con BeautifulSoup
soup = BeautifulSoup(html, 'html.parser')

# Listado de contenedores de vehículos
listings = soup.find_all('div', class_='c-results__content')

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
    title = listing.find('h2', class_='c-results__header-title').text.strip() if listing.find('h2', class_='c-results__header-title') else 'N/A'
    carsubtitle = listing.find('p', class_='c-results-details__description-text c-results-details__description-text--subtitle').text.strip() if listing.find('p', class_='c-results-details__description-text c-results-details__description-text--subtitle') else 'N/A'

    price = listing.find('div', class_='c-results-mount__price').text.strip() if listing.find('div', class_='c-results-mount__price') else 'N/A'
    link = 'https://neoauto.com/' + listing.find('a', class_='c-results-slider__img-box')['href'] if listing.find('a', class_='c-results-slider__img-box') else 'N/A'
    year = title[-4:] # listing.find('span', class_='year').text.strip() if listing.find('span', class_='year') else 'N/A'
    gastypetransmision = (listing.find('p', class_='c-results-details__description-text').text.strip() if listing.find('p', 'c-results-details__description-text') else 'N/A').split("|")    
    location = listing.find('span', class_='c-results-details__description-text c-results-details__description-text--highlighted').text.strip() if listing.find('span', 'c-results-details__description-text c-results-details__description-text--highlighted') else 'N/A'
    
    mileage = "" #listing.find('div', class_='c-results-mount__price').text.strip() if listing.find('div', class_='c-results-mount__price') else 'N/A'""

    detaillistings = listing.find_all('p', class_='c-results-details__description-text')
    #print(f"Number of detail listings found: {len(detaillistings)}")

    for detail in detaillistings:
        if detail.find('span', class_='c-results-used__subtitle-description'):
            mileage = detail.text.strip()
            break

    titles.append(title)
    carsubtitles.append(carsubtitle)
    prices.append(price)
    links.append(link)
    years.append(year)
    gastype.append(gastypetransmision[0])
    transmision.append(gastypetransmision[1])
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
    'gastype': gastype,
    'transmision': transmision,
    'Location': locations
}

df = pd.DataFrame(data)

# Guardar los datos en un archivo CSV
df.to_csv('neoauto_vehicles.csv', index=False)

print("Datos extraídos y guardados en neoauto_vehicles.csv")
