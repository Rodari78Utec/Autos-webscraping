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
    time.sleep(2)

    # Obtener el contenido HTML de la página
    html = driver.page_source

    # Cerrar el navegador
    driver.quit()

    # Imprimir el HTML para verificar que se cargó correctamente
    #with open("outputautocosmos.html", "w", encoding='utf-8') as file:
    #   file.write(html)


    # Analizar el contenido HTML con BeautifulSoup
   

    return BeautifulSoup(html, 'html.parser')

    
# Iniciar el navegador

def extrac_gastype_transmision(url):
    
    soup = get_html_from_page(url)
    fuel_type = ""
    transmission = ""
    color = ""
    cilinder = ""
    upholstery = ""
    engine= ""

    divs = soup.find_all('div', class_='car-specifics__extra-info')
    #print (listings)
    for div in divs:
        spans = div.find_all('span')
        for span in spans:
            if span['itemprop']=='color':
                color= span.text.strip()
                break


    listings = soup.find_all('table', class_='ficha')
    for listing in listings:
        rows = listing.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            if len(cols) == 2:
                
                if 'Cilindrada' in cols[0].text:
                    engine = cols[1].text.strip()
                if 'Combustible' in cols[0].text:
                    fuel_type = cols[1].text.strip()
                if 'Cilindros' in cols[0].text:
                    cilinder = cols[1].text.strip()
                if 'Transmisión' in cols[0].text:
                    transmission = cols[1].text.strip()                
                if 'Tapicería' in cols[0].text:
                    upholstery = cols[1].text.strip()
                    break
        if upholstery!="":
            break

    return fuel_type, transmission, color, cilinder, upholstery, engine

def extract_data_from_page(url):

    soup = get_html_from_page(url)


    # Listado de contenedores de vehículos
    listings = soup.find_all('article', class_='card listing-card')

    # Imprimir el número de listados encontrados
    print(f"Number of listings found: {len(listings)}")

    # Variables para almacenar datos
    brands = []
    models =[]
    versions =[]
    currencies =[]
    prices = []
    links = []
    years = []
    kms = []
    gastypes =[]
    transmisions =[]
    locations = []
    colors = []
    cilinders = []
    upholsteries = []
    engines =[]

    # Extraer datos de cada contenedor
    for listing in listings:
        brand = listing.find('span', class_='listing-card__brand').text.strip() if listing.find('span', class_='listing-card__brand') else 'N/A'
        model = listing.find('span', class_='listing-card__model').text.strip() if listing.find('span', class_='listing-card__model') else 'N/A'
        version = listing.find('span', class_='listing-card__version').text.strip() if listing.find('span', class_='listing-card__version') else 'N/A'

        year =  listing.find('span', class_='listing-card__year').text.strip() if listing.find('span', class_='listing-card__year') else 'N/A'
        km = listing.find('span', class_='listing-card__km').text.strip() if listing.find('span', class_='listing-card__km') else 'N/A'

        currency = listing.find('span', class_='listing-card__price').find('meta')['content'] if listing.find('span', class_='listing-card__price').find('meta') else 'N/A'

        
        price = listing.find('span', class_='listing-card__price-value').text.strip() if listing.find('span', class_='listing-card__price-value') else 'N/A'


        
        link =  listing.find('figure', class_='listing-card__image').find('img')['content'] if listing.find('figure', class_='listing-card__image').find('img') else 'N/A'

        
        location = listing.find('span', class_='listing-card__city').text.strip() if listing.find('span', 'listing-card__city') else 'N/A'
        location = location + listing.find('span', class_='listing-card__province').text.strip() if listing.find('span', 'listing-card__province') else 'N/A'


        
        url_detail = "https://www.autocosmos.com.pe"+listing.find('a')['href'] if listing.find('a') else 'N/A'
        gastype, transmision, color, cilinder, upholstery, engine = extrac_gastype_transmision (url_detail)

        brands.append(brand)
        models.append(model)
        versions.append(version)
        currencies.append(currency)
        prices.append(price)
        links.append(link)
        years.append(year)
        kms.append (km)
        gastypes.append	(gastype)
        transmisions.append(transmision)
        locations.append(location)
        colors.append(color)
        cilinders.append(cilinder)
        upholsteries.append(upholstery)
        engines.append(engine)
        

        
    # Crear un DataFrame con los datos extraídos
    return {
        'Brands' :brands,
        'Models' :models,
        'Version' :versions ,
        'Currency' :currencies,
        'Price' :prices,
        'Urlpic' :links,
        'Year' :years,
        'KM' :kms,
        'Fuel_type' :gastypes,
        'Transmission' :transmisions,
        'Location' :locations,
        'Color' : colors,
        'Cilinders' : cilinders,
        'Upholstery': upholsteries,
        'Engine' : engines
    }

    

# Iterar sobre las páginas y extraer datos
all_data = {'Brands': [], 'Models': [], 'Version': [], 'Currency': [], 'Price': [], 'Urlpic': [], 'Year': [], 'KM': [], 'Fuel_type': [],'Transmission': [], 'Location': [], 'Color': [], 'Cilinders': [], 'Upholstery': [], 'Engine': []}

for page_number in range(1, 34):  # Iterar desde 1 hasta 285
    url = f'https://www.autocosmos.com.pe/auto/usado?pidx={page_number}'
    data = extract_data_from_page(url)
    #print(data)
    for key in all_data.keys():
        all_data[key].extend(data[key])

# Crear un DataFrame con los datos extraídos
df = pd.DataFrame(all_data)

# Guardar los datos en un archivo CSV
df.to_csv('autocosmos_vehicles.csv', index=False)

print("Datos extraídos y guardados en neoauto_vehicles.csv")
