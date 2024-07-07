from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import time
import json

# Configuración del navegador
options = Options()
options.add_argument('--headless')  # Ejecutar en modo headless (sin abrir una ventana del navegador)
options.binary_location = '/usr/bin/chromium-browser'  # Ubicación del binario de Chromium
chromedriver_path = '/usr/lib/chromium-browser/chromedriver'  # Ubicación del chromedriver

def get_html_from_page(url):
    """Obtiene el contenido HTML de una página web."""
    driver = webdriver.Chrome(service=Service(chromedriver_path), options=options)
    driver.get(url)
    time.sleep(2)
    html = driver.page_source
    driver.quit()
    return BeautifulSoup(html, 'html.parser')

def extract_data_from_json(url):
    """Extrae datos de un JSON embebido en la página web."""
    soup = get_html_from_page(url)
    data = json.loads(soup.find('script', {'id': '__NEXT_DATA__'}).string)

    detail = data['props']['pageProps']['initialState']['advertisement']['detail']
    brand = detail.get('brandName', '')
    model = detail.get('modelName', '')
    year = detail.get('modelYear', '')
    transmission = detail.get('transmissionName', '')
    km = detail.get('mileage', '')
    photos = detail.get('photos', [])
    link = photos[0].get('medium', '') if photos else ''

    features_secondary = detail.get('features', {}).get('secondary', [])
    color = next((item['value'] for item in features_secondary if item['name'] == "Color"), "")
    version = next((item['value'] for item in features_secondary if item['name'] == "Tracción"), "")
    cilinder = next((item['value'] for item in features_secondary if item['name'] == "Número cilindros"), "")

    features_main = detail.get('features', {}).get('main', [])
    gastype = next((item['value'] for item in features_main if item['name'] == "Combustible"), "")
    engine = next((item['value'] for item in features_main if item['name'] == "Cilindrada"), "")
    version = next((item['value'] for item in features_main if item['name'] == "Versión"), version)

    accessories = detail.get('accessories', [])
    upholstery = next((item['name'] for accessory in accessories if accessory['name'] == "Extras" for item in accessory['items']), "tela")
    if upholstery != "Asientos de cuero":
        upholstery = "tela"
    
    return brand, model, version, year, gastype, transmission, color, upholstery, km, cilinder, engine, link

def extract_data_from_page(url):
    """Extrae datos de una página de listados de vehículos."""
    soup = get_html_from_page(url)
    listings = soup.find_all('div', class_='c-results__content')

    data = {
        'Brands': [], 'Models': [], 'Version': [], 'Currency': [], 'Price': [],
        'Urlpic': [], 'Year': [], 'KM': [], 'Fuel_type': [], 'Transmission': [],
        'Location': [], 'Color': [], 'Cilinder': [], 'Upholstery': [], 'Engine': []
    }

    for listing in listings:
        price = listing.find('div', class_='c-results-mount__price').text.strip() if listing.find('div', class_='c-results-mount__price') else 'N/A'
        detallelink = 'https://neoauto.com/' + listing.find('a', class_='c-results-slider__img-box')['href'] if listing.find('a', class_='c-results-slider__img-box') else 'N/A'
        location = listing.find('span', class_='c-results-details__description-text c-results-details__description-text--highlighted').text.strip() if listing.find('span', 'c-results-details__description-text c-results-details__description-text--highlighted') else 'N/A'
        currency = "USD"
        print (detallelink)
        brand, model, version, year, gastype, transmission, color, upholstery, km, cilinder, engine, link = extract_data_from_json(detallelink)
        
        data['Brands'].append(brand)
        data['Models'].append(model)
        data['Version'].append(version)
        data['Currency'].append(currency)
        data['Price'].append(price)
        data['Urlpic'].append(link)
        data['Year'].append(year)
        data['KM'].append(km)
        data['Fuel_type'].append(gastype)
        data['Transmission'].append(transmission)
        data['Location'].append(location)
        data['Color'].append(color)
        data['Cilinder'].append(cilinder)
        data['Upholstery'].append(upholstery)
        data['Engine'].append(engine)
    
    return data

def main():
    """Función principal para extraer y guardar datos en un archivo CSV."""
    all_data = {'Brands': [], 'Models': [], 'Version': [], 'Currency': [], 'Price': [], 'Urlpic': [], 'Year': [], 'KM': [], 'Fuel_type': [], 'Transmission': [], 'Location': [], 'Color': [], 'Cilinder': [], 'Upholstery': [], 'Engine': []}

    for page_number in range(1, 2):  # Iterar desde 1 hasta 280
        url = f'https://neoauto.com/venta-de-autos-usados?page={page_number}'
        print(url)
        data = extract_data_from_page(url)
        for key in all_data.keys():
            all_data[key].extend(data[key])

    df = pd.DataFrame(all_data)
    df.to_csv('neoauto_vehicles_total.csv', index=False)
    print("Datos extraídos y guardados en neoauto_vehicles_total.csv")

if __name__ == "__main__":
    main()
