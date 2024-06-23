from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException  # Importar TimeoutException
from bs4 import BeautifulSoup
import pandas as pd
import time
import json

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

def extract_data_from_json(url):
    soup = get_html_from_page(url)
    
    brand, model, version, year, gastype, transmission, color, upholstery, km, cilinder, engine, link = "", "", "", "", "", "", "", "", "", "", "",""

    script = soup.find('script', {'id': '__NEXT_DATA__'})
    if script:
        data = json.loads(script.string)
        # Extraer datos relevantes desde el JSON
        try:
            detail = data['props']['pageProps']['initialState']['advertisement']['detail']
            brand = detail.get('brandName', '')
            model = detail.get('modelName', '')
            year = detail.get('modelYear', '')
            # gastype = detail.get('fuel', {}).get('name', '')
            transmission = detail.get('transmissionName', '')                    
            km = detail.get('mileage', '')
            #engine= detail['features']['main'][4].get('value', '')  # Assuming index 6 is mortor                        
            photos = detail.get('photos', [])
            if photos and len(photos) > 0:
                link = photos[0].get('medium', '')
            # cilinder = detail['features']['secondary'][6].get('value', '')  # Assuming index 6 is cilinder
            # version =detail['features']['secondary'][4].get('value', '')  # Assuming index 6 is version            
            # color = detail['features']['secondary'][5].get('value', '')  # Assuming index 5 is color

            features_secondary = detail.get('features', {}).get('secondary', [])
            for secondary in features_secondary:              
                if secondary['name'] == "Color":
                    color = secondary['value']
                if secondary['name'] == "Tracción":
                    version = secondary['value']
                if secondary['name'] == "Número cilindros":
                    cilinder = secondary['value']

            features_main = detail.get('features', {}).get('main', [])
            for main in features_main:    
                if main['name'] == "Combustible":
                    gastype= main['value']
                if main['name'] == "Cilindrada":
                    engine = main['value']
                if main['name'] == "Versión":
                    version = main['value']

            accessories = detail.get('accessories', [])
            upholstery = ""
            for accessory in accessories:
                if accessory['name'] == "Extras":
                    upholstery = accessory['items'][0]['name']
                    break
            if upholstery!="Asientos de cuero":
                upholstery="tela"
        except KeyError as e:
            print(f"Key not found: {e}")
    
    return brand, model, version, year, gastype, transmission, color, upholstery, km, cilinder, engine, link


# Función para extraer datos de una página
def extract_data_from_page(url):

    soup = get_html_from_page(url)
    # Listado de contenedores de vehículos
    listings = soup.find_all('div', class_='c-results__content')

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
    engines= []
    # Extraer datos de cada contenedor
    for listing in listings:
        
        price = listing.find('div', class_='c-results-mount__price').text.strip() if listing.find('div', class_='c-results-mount__price') else 'N/A'
        
        #link = listing.find('img', class_='c-results-slider__img-inside lozad fade')['src'] if listing.find('img', class_='c-results-slider__img-inside lozad fade') else 'N/A'           
        detallelink = 'https://neoauto.com/' + listing.find('a', class_='c-results-slider__img-box')['href'] if listing.find('a', class_='c-results-slider__img-box') else 'N/A'           
        location = listing.find('span', class_='c-results-details__description-text c-results-details__description-text--highlighted').text.strip() if listing.find('span', 'c-results-details__description-text c-results-details__description-text--highlighted') else 'N/A'
        
        currency = "USD"

        #print (detallelink)
        #Brands,Models,Version,Currency
        
        brand, model, version, year, gastype, transmission, color, upholstery, km, cilinder, engine, link = extract_data_from_json(detallelink)
        #print(link)
        
        brands.append(brand)
        models.append(model)
        versions.append(version)
        currencies.append(currency)
        prices.append(price)
        links.append(link)
        years.append(year)
        kms.append (km)
        gastypes.append	(gastype)
        transmisions.append(transmission)
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
        'Cilinder' : cilinders,
        'Upholstery': upholsteries,
        'Engine' : engines
    }

# Iterar sobre las páginas y extraer datos
all_data = {'Brands': [], 'Models': [], 'Version': [], 'Currency': [], 'Price': [], 'Urlpic': [], 'Year': [], 'KM': [], 'Fuel_type': [],'Transmission': [], 'Location': [],'Color': [], 'Cilinder':[], 'Upholstery':[], 'Engine':[]}

for page_number in range(1, 281):  # Iterar desde 1 hasta 280
    url = f'https://neoauto.com/venta-de-autos-usados?page={page_number}'
    print(url)
    data = extract_data_from_page(url)
    for key in all_data.keys():
        all_data[key].extend(data[key])

# Crear un DataFrame con los datos extraídos
df = pd.DataFrame(all_data)

# Guardar los datos en un archivo CSV
df.to_csv('neoauto_vehicles_total.csv', index=False)

print("Datos extraídos y guardados en neoauto_vehicles.csv")
