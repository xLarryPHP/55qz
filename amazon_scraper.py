import time
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from compare_prices import compare_prices

# Fonction pour lire les URLs depuis le fichier config.txt
def read_config_file(file_path="config.txt"):
    with open(file_path, "r") as file:
        urls = file.readlines()
    return [url.strip() for url in urls]

# Fonction pour gérer les cookies
def handle_cookies(driver):
    try:
        accept_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "sp-cc-accept"))
        )
        accept_button.click()
        time.sleep(1)
    except:
        pass

# Fonction pour passer à la page suivante avec gestion du défilement et attente explicite
def go_to_next_page(driver):
    try:
        # Gérer les cookies avant d'essayer de cliquer sur "Suivant"
        handle_cookies(driver)

        # Utilisation de la classe spécifique du bouton "Suivant"
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.s-pagination-next'))
        )

        # Faire défiler jusqu'au bouton "Suivant" pour le rendre visible
        actions = ActionChains(driver)
        actions.move_to_element(next_button).perform()

        # Cliquer sur le bouton une fois qu'il est visible et interactable
        next_button.click()

        # Pause pour laisser la page se charger
        time.sleep(3)
        return True

    except Exception as e:
        print(f"Erreur lors de la tentative de passage à la page suivante : {e}")
        return False

# Fonction pour extraire le code ASIN et le prix sur une page Amazon
def extract_product_data(driver):
    products = driver.find_elements(By.XPATH, "//div[@data-cy='asin-faceout-container']")
    product_data = []

    for product in products:
        try:
            link_element = product.find_element(By.CSS_SELECTOR, "a.a-link-normal")
            product_link = link_element.get_attribute("href")
            asin = product_link.split("/dp/")[1].split("/")[0]

            # Extraire le prix
            price_whole = product.find_element(By.CSS_SELECTOR, "span.a-price-whole").text.strip()
            price_fraction = product.find_element(By.CSS_SELECTOR, "span.a-price-fraction").text.strip()
            amazon_price = f"{price_whole}.{price_fraction}".replace(",", ".").replace("€", "").replace(" ", "")

            product_data.append((asin, amazon_price))
        except Exception as e:
            print(f"Erreur lors de l'extraction des données du produit : {e}")
            continue

    return product_data

# Fonction pour traiter un seul lien
def process_amazon_link(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        driver.get(url)
        time.sleep(3)  # Simuler un comportement réaliste

        page_count = 0

        while True:
            # Extraire les produits
            product_data_list = extract_product_data(driver)

            # Pour chaque produit trouvé
            for asin, amazon_price in product_data_list:
                print(f"Produit trouvé : ASIN {asin}, Prix Amazon : {amazon_price}€")
                # Comparaison avec Keepa
                compare_prices(asin, amazon_price)

            # Tenter de passer à la page suivante
            if not go_to_next_page(driver):
                # Si aucune page suivante n'est disponible, revenir à la première page
                page_count += 1
                print(f"Recommencer à la première page après avoir parcouru {page_count} pages.")
                driver.get(url)
                time.sleep(3)

    except Exception as e:
        print(f"Erreur lors du traitement de l'URL {url} : {e}")
    finally:
        driver.quit()

# Fonction principale pour exécuter plusieurs threads
def run_threads(urls, num_threads=5):
    threads = []
    for i in range(num_threads):
        if i < len(urls):
            t = threading.Thread(target=process_amazon_link, args=(urls[i],))
            threads.append(t)
            t.start()

    # Attendre que tous les threads soient terminés
    for t in threads:
        t.join()

# Lecture des URLs depuis le fichier config.txt
urls = read_config_file()

# Lancer les threads
run_threads(urls, num_threads=5)