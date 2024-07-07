from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
import concurrent.futures
import time

# Configuración del navegador
options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--profile-directory=Default')
options.add_argument('--user-data-dir=~/.config/google-chrome')
options.binary_location = '/usr/bin/chromium-browser'  # Ubicación del binario de Chromium

# Función para iniciar y configurar el driver
def init_driver():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

# Función para extraer datos de una página
def get_html_from_page(url, driver):
    driver.get(url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'article.card.listing-card')))
    html = driver.page_source
    return BeautifulSoup(html, 'html.parser')

def extract_gastype_transmission(url, driver):
    soup = get_html_from_page(url, driver)
    fuel_type = transmission = color = cilinder = upholstery = 'N/A'

    divs = soup.find_all('div', class_='car-specifics__extra-info')
    for div in divs:
        spans = div.find_all('span')
        for span in spans:
            if span.get('itemprop') == 'color':
                color = span.text.strip()

    listings = soup.find_all('table', class_='ficha')
    for listing in listings:
        rows = listing.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            if len(cols) == 2:
                if 'Combustible' in cols[0].text:
                    fuel_type = cols[1].text.strip()
                if 'Cilindros' in cols[0].text:
                    cilinder = cols[1].text.strip()
                if 'Transmisión' in cols[0].text:
                    transmission = cols[1].text.strip()
                if 'Tapicería' in cols[0].text:
                    upholstery = cols[1].text.strip()
                    break
            if upholstery != 'N/A':
                break

    return fuel_type, transmission, color, cilinder, upholstery

def extract_data_from_page(url, driver):
    soup = get_html_from_page(url, driver)

    listings = soup.find_all('article', class_='card listing-card')
    data = []

    for listing in listings:
        try:
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

            gastype, transmision, color, cilinder, upholstery = extract_gastype_transmission(url_detail, driver)

            data.append({
                'Brand': brand,
                'Model': model,
                'Version': version,
                'Currency': currency,
                'Price': price,
                'Urlpic': link,
                'Year': year,
                'KM': km,
                'Fuel_type': gastype,
                'Transmission': transmision,
                'Location': location,
                'Color': color,
                'Cilinders': cilinder,
                'Upholstery': upholstery
            })
        except Exception as e:
            print(f"Error processing listing: {e}")

    return data

def scrape_page_range(start, end):
    driver = init_driver()
    all_data = []

    for page_number in range(start, end):
        url = f'https://www.autocosmos.com.pe/auto/usado?pidx={page_number}'
        data = extract_data_from_page(url, driver)
        all_data.extend(data)

    driver.quit()
    return all_data

def main():
    total_data = []

    # Ajusta el rango de páginas según tus necesidades
    page_ranges = [(1, 11), (11, 21), (21, 31), (31, 34)] # Divide las páginas en rangos

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(scrape_page_range, start, end) for start, end in page_ranges]
        for future in concurrent.futures.as_completed(futures):
            total_data.extend(future.result())

    df = pd.DataFrame(total_data)
    df.to_csv('autocosmos_vehicles.csv', index=False)
    print("Datos extraídos y guardados en neoauto_vehiclesautocosmos.csv")

if __name__ == "__main__":
    main()
