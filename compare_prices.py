import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def extract_keepa_price(asin):
    # URL correcte de la page Keepa
    keepa_url = f"https://keepa.com/#!product/4-{asin}"
    
    # Configuration de Selenium avec WebDriver Manager
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Activer le mode headless pour que Chrome ne soit pas visible
    chrome_options.add_argument("--no-sandbox")  # Nécessaire sur certaines distributions Linux
    chrome_options.add_argument("--disable-dev-shm-usage")  # Evite les problèmes de ressources dans certains environnements
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])  # Désactiver les logs
    chrome_options.add_argument("--enable-javascript")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])  # Désactiver les logs
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Lancement du navigateur Chrome en mode invisible
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        # Visiter la page produit Keepa avec l'URL correcte
        driver.get(keepa_url)
        time.sleep(5)  # Attendre que la page se charge

        # Vérifier si l'élément statisticsContent existe
        statistics_content = driver.find_element(By.ID, 'statisticsContent')
        if statistics_content:
            print("L'élément 'statisticsContent' est trouvé.")
            driver.execute_script("document.getElementById('statisticsContent').style.display = 'block';")
        else:
            print("L'élément 'statisticsContent' est introuvable.")
            return None

        # Attendre que l'élément contenant le prix des 90 derniers jours apparaisse
        wait = WebDriverWait(driver, 10)
        average_90d_element = wait.until(EC.visibility_of_element_located((By.XPATH, "//td[@class='statsRow2'][span[contains(text(), 'last 90 days')]]")))
        average_90d_price = average_90d_element.text.split("\n")[0].replace("€", "").strip()  # Extraire juste le prix et retirer "€"
        
        return average_90d_price
    except Exception as e:
        print(f"Erreur lors de l'extraction des prix Keepa: {e}")
        return None
    finally:
        driver.quit()

# Fonction de comparaison des prix
def compare_prices(asin, amazon_price):
    keepa_price = extract_keepa_price(asin)
    
    if keepa_price:
        print(f"Prix Amazon : {amazon_price}€")
        print(f"Prix Keepa sur 90 jours : {keepa_price}€")
        
        try:
            # Convertir les prix en float pour faire la comparaison
            amazon_price_float = float(amazon_price.replace("€", "").replace(",", ".").strip())
            keepa_price_float = float(keepa_price.strip())
            
            if amazon_price_float < keepa_price_float:
                print("Le prix Amazon est inférieur au prix moyen Keepa.")
            elif amazon_price_float > keepa_price_float:
                print("Le prix Amazon est supérieur au prix moyen Keepa.")
            else:
                print("Le prix Amazon est égal au prix moyen Keepa.")
            
            # Calculer la différence en pourcentage
            difference_percentage = ((keepa_price_float - amazon_price_float) / keepa_price_float) * 100
            print(f"Le prix Amazon est inférieur de {difference_percentage:.2f}% par rapport au prix moyen Keepa.")
        
        except ValueError:
            print("Erreur de conversion des prix.")
    else:
        print("Impossible de récupérer le prix Keepa.")

