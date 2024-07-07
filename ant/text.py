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

            # Verificar la existencia de fotos y obtener el enlace de la primera foto
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

# URL del auto usado en Neoauto


url = "https://neoauto.com/auto/usado/chevrolet-onix-2022-1788517"
brand, model, version, year, gastype, transmission, color, upholstery, km, cilinder, engine, link  = extract_data_from_json(url)

# Imprimir los datos extraídos
print(f"Marca: {brand}")
print(f"Modelo: {model}")
print(f"version: {version}")
print(f"Año: {year}")
print(f"Tipo de combustible: {gastype}")
print(f"Transmisión: {transmission}")
print(f"Color: {color}")
print(f"Tapicería: {upholstery}")
print(f"Kilometraje: {km}")
print(f"Cilindros: {cilinder}")
print(f"motor: {engine}")
