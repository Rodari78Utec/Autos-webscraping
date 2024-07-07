from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException  # Importar TimeoutException
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

    # Esperar explícitamente a que un elemento específico se cargue
    try:
        element_present = EC.presence_of_element_located((By.CSS_SELECTOR, 'selector_del_elemento_dinamico'))
        WebDriverWait(driver, 20).until(element_present)
    except TimeoutException:
        print("Timed out waiting for page to load")

    # Obtener el contenido HTML de la página
    html = driver.page_source

    # Cerrar el navegador
    driver.quit()

    # Guardar el HTML para verificar que se cargó correctamente
    with open("outputautocosmos.html", "w", encoding='utf-8') as file:
        file.write(html)

    # Analizar el contenido HTML con BeautifulSoup
    return BeautifulSoup(html, 'html.parser')


def extrac_gastype_transmision(url):
    
    soup = get_html_from_page(url)
    

    brand, model, version, year, gastype, transmission, color, upholstery, km, cilinder = "", "", "", "", "", "", "", "", "", ""

    listings = soup.find_all('div', class_='block box-border')
    for listing in listings:
        cols = listing.find_all('div')
        if len(cols) == 2:
            if 'Año Modelo' in cols[0].text:
                year= cols[1].text.strip()  
            if 'Kilometraje' in cols[0].text:
                km= cols[1].text.strip()  
            if 'Transmisión' in cols[0].text:
                transmission= cols[1].text.strip()  
            if 'Combustible' in cols[0].text:
                gastype= cols[1].text.strip()            
            if 'Cilindrada' in cols[0].text:
                cilinder = cols[1].text.strip()            
                break
        if cilinder!="":
            break
    listings = soup.find_all('div', class_='flex flex-col items-start gap-[10px] py-2 box-border md:py-[10px]')
    print (listings)
    for listing in listings:
        cols = listing.find_all('div')
        
        if len(cols) == 2:
            if 'Marca' in cols[0].text:
                brand= cols[1].text.strip()  
            if 'Modelo' in cols[0].text:
                model= cols[1].text.strip()  
            if 'Tracción' in cols[0].text:
                version= cols[1].text.strip()           
            if 'Color' in cols[0].text:
                color = cols[1].text.strip()            
                break
        if color!="":
            break

    listings = soup.find_all('div', class_='sc-bxSTMQ geowOX')
    for listing in listings:
        
        seccion = listing.find('span', class_='font-ubuntu font-bold text-base md:text-lg md:leading-6').text.strip() if listing.find('span', 'font-ubuntu font-bold text-base md:text-lg md:leading-6') else 'N/A'
        if seccion== "Extras":
            divisiones = listing.find_all('flex h-10 items-start font-ubuntu text-base leading-[18px] text-black md:h-11 md:text-lg md:leading-6')
            for division in divisiones:
                if division.text.strip()=="Asientos de cuero":
                    upholstery = division.text.strip()
                if upholstery!="":
                    break            
            if upholstery=="":
                upholstery = "tela"
            break
    return brand, model, version, year, gastype, transmission, color, cilinder, upholstery , km

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

    # Extraer datos de cada contenedor
    for listing in listings:
        
        price = listing.find('div', class_='c-results-mount__price').text.strip() if listing.find('div', class_='c-results-mount__price') else 'N/A'
        
        link = listing.find('img', class_='c-results-slider__img-inside lozad fade')['src'] if listing.find('img', class_='c-results-slider__img-inside lozad fade') else 'N/A'           
        detallelink = 'https://neoauto.com/' + listing.find('a', class_='c-results-slider__img-box')['href'] if listing.find('a', class_='c-results-slider__img-box') else 'N/A'           
        location = listing.find('span', class_='c-results-details__description-text c-results-details__description-text--highlighted').text.strip() if listing.find('span', 'c-results-details__description-text c-results-details__description-text--highlighted') else 'N/A'
        
        # print(f"Number of detail listings found: {len(detaillistings)}")

        currency = "USD"

        print (detallelink)
        #Brands,Models,Version,Currency
        brand, model, version, year, gastype, transmision, color, cilinder, upholstery, km = extrac_gastype_transmision(detallelink)
        
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
        break;
                
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
        'Upholstery': upholsteries
    }

# Iterar sobre las páginas y extraer datos
all_data = {'Brands': [], 'Models': [], 'Version': [], 'Currency': [], 'Price': [], 'Urlpic': [], 'Year': [], 'KM': [], 'Fuel_type': [],'Transmission': [], 'Location': []}

for page_number in range(1, 2):  # Iterar desde 1 hasta 285
    url = f'https://neoauto.com/venta-de-autos-usados?page={page_number}'
    data = extract_data_from_page(url)
    for key in all_data.keys():
        all_data[key].extend(data[key])

# Crear un DataFrame con los datos extraídos
df = pd.DataFrame(all_data)

# Guardar los datos en un archivo CSV
df.to_csv('neoauto_vehicles_total.csv', index=False)

print("Datos extraídos y guardados en neoauto_vehicles.csv")
