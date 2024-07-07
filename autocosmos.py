from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import time

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

def extrac_gastype_transmision(url):
    """Extrae el tipo de combustible, transmisión, color, cilindrada, tapicería y motor de la página de detalles."""
    soup = get_html_from_page(url)
    fuel_type, transmission, color, cilinder, upholstery, engine = "", "", "", "", "", ""

    for div in soup.find_all('div', class_='car-specifics__extra-info'):
        for span in div.find_all('span'):
            if span.get('itemprop') == 'color':
                color = span.text.strip()
                break

    for listing in soup.find_all('table', class_='ficha'):
        for row in listing.find_all('tr'):
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
        if upholstery:
            break

    return fuel_type, transmission, color, cilinder, upholstery, engine

def extract_data_from_page(url):
    """Extrae los datos de los listados de vehículos de una página."""
    soup = get_html_from_page(url)
    listings = soup.find_all('article', class_='card listing-card')
    print(f"Number of listings found: {len(listings)}")

    data = {
        'Brands': [], 'Models': [], 'Version': [], 'Currency': [], 'Price': [],
        'Urlpic': [], 'Year': [], 'KM': [], 'Fuel_type': [], 'Transmission': [],
        'Location': [], 'Color': [], 'Cilinders': [], 'Upholstery': [], 'Engine': []
    }

    for listing in listings:
        brand = listing.find('span', class_='listing-card__brand').text.strip() if listing.find('span', class_='listing-card__brand') else 'N/A'
        model = listing.find('span', class_='listing-card__model').text.strip() if listing.find('span', class_='listing-card__model') else 'N/A'
        version = listing.find('span', class_='listing-card__version').text.strip() if listing.find('span', class_='listing-card__version') else 'N/A'
        year = listing.find('span', class_='listing-card__year').text.strip() if listing.find('span', class_='listing-card__year') else 'N/A'
        km = listing.find('span', class_='listing-card__km').text.strip() if listing.find('span', class_='listing-card__km') else 'N/A'
        currency = listing.find('span', class_='listing-card__price').find('meta')['content'] if listing.find('span', class_='listing-card__price').find('meta') else 'N/A'
        price = listing.find('span', class_='listing-card__price-value').text.strip() if listing.find('span', class_='listing-card__price-value') else 'N/A'
        link = listing.find('figure', class_='listing-card__image').find('img')['content'] if listing.find('figure', class_='listing-card__image').find('img') else 'N/A'
        location = listing.find('span', class_='listing-card__city').text.strip() if listing.find('span', 'listing-card__city') else 'N/A'
        location += listing.find('span', class_='listing-card__province').text.strip() if listing.find('span', 'listing-card__province') else 'N/A'
        url_detail = "https://www.autocosmos.com.pe" + listing.find('a')['href'] if listing.find('a') else 'N/A'

        print(url_detail)
        
        
        gastype, transmission, color, cilinder, upholstery, engine = extrac_gastype_transmision(url_detail)

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
        data['Cilinders'].append(cilinder)
        data['Upholstery'].append(upholstery)
        data['Engine'].append(engine)
    
    return data

def main():
    """Función principal para extraer y guardar datos en un archivo CSV."""
    all_data = {
        'Brands': [], 'Models': [], 'Version': [], 'Currency': [], 'Price': [], 
        'Urlpic': [], 'Year': [], 'KM': [], 'Fuel_type': [], 'Transmission': [], 
        'Location': [], 'Color': [], 'Cilinders': [], 'Upholstery': [], 'Engine': []
    }

    for page_number in range(1, 2):  # Iterar desde 1 hasta 33
        url = f'https://www.autocosmos.com.pe/auto/usado?pidx={page_number}'
        data = extract_data_from_page(url)
        for key in all_data.keys():
            all_data[key].extend(data[key])

    df = pd.DataFrame(all_data)
    df.to_csv('autocosmos_vehicles.csv', index=False)
    print("Datos extraídos y guardados en autocosmos_vehicles.csv")

if __name__ == "__main__":
    main()
